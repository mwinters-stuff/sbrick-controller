import gi

from SBrickConfigureDialog import SBrickConfigureDialog
from SBrickFunctionsBox import SBrickFunctionsBox
from SBrickSequenceBox import SBrickSequenceBox

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk, GLib, Gio, GObject

from SBrickInfoBox import SBrickInfoBox
from SBrickMotorChannelBox import SBrickMotorChannelBox
from SBrickCommunications import SBrickCommunications
from SBrickServoChannelBox import SBrickServoChannelBox


class SBrickBox(Gtk.Box):
    def __init__(self, sbrick_configuration):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=3, margin=0)
        self.sbrickConfiguration = sbrick_configuration

        self.topBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3, margin=0)

        # self.buttonSettings = Gtk.Button.new_with_label("Settings")
        self.buttonSettings = Gtk.Button.new_with_label("Settings")
        self.buttonSettings.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_PREFERENCES, Gtk.IconSize.BUTTON))
        self.buttonSettings.connect("clicked", self.on_button_settings_clicked)
        self.topBox.pack_start(self.buttonSettings, False, True, 0)

        self.labelBrickName = Gtk.Label("SBrick: %s" % self.sbrickConfiguration["name"])
        self.labelBrickAddress = Gtk.Label("Address: %s" % self.sbrickConfiguration["addr"])
        self.topBox.pack_start(self.labelBrickName, False, True, 0)
        self.topBox.pack_start(self.labelBrickAddress, True, False, 0)

        self.buttonConnect = Gtk.Button.new_with_label("Connect")

        self.buttonConnect.connect("clicked", self.on_button_connect_clicked)
        self.topBox.pack_start(self.buttonConnect, False, True, 0)

        self.buttonEStop = Gtk.Button.new_with_label("!!!STOP!!!")

        self.buttonEStop.connect("clicked", self.on_button_estop_clicked)
        self.topBox.pack_start(self.buttonEStop, False, True, 0)
        self.buttonEStop.set_sensitive(False)

        self.pack_start(self.topBox, False, True, 0)

        self.notebook = Gtk.Notebook()
        self.pack_start(self.notebook, True, True, 0)
        self.notebook.set_scrollable(True)

        self.SBrickInfoBox = SBrickInfoBox()

        self.notebook.append_page(self.SBrickInfoBox, Gtk.Label("Information"))

        self.password_guest = None
        self.password_owner = None
        self.currentSBrickChannels = []
        self.sbrickCommunications = None

        if "ownerPassword" in self.sbrickConfiguration:
            self.password_owner = self.sbrickConfiguration["ownerPassword"]
        if "guestPassword" in self.sbrickConfiguration:
            self.password_guest = self.sbrickConfiguration["guestPassword"]

        self.channelBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=5)
        self.notebook.append_page(self.channelBox, Gtk.Label("Control"))

        self.show_channels()

        if "functions" not in self.sbrickConfiguration:
            self.sbrickConfiguration["functions"] = dict()
        self.SBrickFunctionsBox = SBrickFunctionsBox(self.sbrickConfiguration["functions"],
                                                     self.sbrickConfiguration["channelConfiguration"])
        self.notebook.append_page(self.SBrickFunctionsBox, Gtk.Label("Functions"))

        self.SBrickSequenceBox = SBrickSequenceBox(self.sbrickConfiguration)
        self.notebook.append_page(self.SBrickSequenceBox, Gtk.Label("Sequence"))

        self.show_all()

    def disconnect(self):
        if self.sbrickCommunications:
            self.sbrickCommunications.disconnect()

    def get_sbrick_communications(self):
        return self.sbrickCommunications

    def get_connected(self):
        return self.sbrickCommunications is not None

    def set_password_owner(self, password):
        self.password_owner = password

    def set_password_guest(self, password):
        self.password_guest = password

    def write_owner_password(self):
        if self.sbrickCommunications is not None:
            self.sbrickCommunications.set_owner_password(self.password_owner)

    def write_guest_password(self):
        if self.sbrickCommunications is not None:
            self.sbrickCommunications.set_guest_password(self.password_guest)

    def clear_owner_password(self):
        if self.sbrickCommunications is not None:
            self.sbrickCommunications.clear_owner_password()

    def clear_guest_password(self):
        if self.sbrickCommunications is not None:
            self.sbrickCommunications.clear_guest_password()

    # noinspection PyUnusedLocal
    def on_button_settings_clicked(self, widget):
        dialog = SBrickConfigureDialog(self.get_toplevel(), self.sbrickConfiguration)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.show_channels()
            self.labelBrickName.set_text("SBrick: %s" % self.sbrickConfiguration["name"])
            self.labelBrickAddress.set_text("Address: %s" % self.sbrickConfiguration["addr"])

        dialog.destroy()

    # noinspection PyUnusedLocal
    def on_button_connect_clicked(self, widget):
        self.buttonConnect.set_sensitive(False)
        if self.sbrickCommunications is None:
            self.buttonConnect.set_label("Connecting...")
            self.sbrickCommunications = SBrickCommunications(self.sbrickConfiguration["addr"])
            for channelNumber in range(4):
                sb = self.sbrickConfiguration["channelConfiguration"][channelNumber]
                self.sbrickCommunications.set_channel_config_id(channelNumber, sb["id"])

            self.sbrickCommunications.connect('sbrick_connected', self.on_sbrick_connected)
            self.sbrickCommunications.connect('sbrick_disconnected_error', self.on_sbrick_disconnected_error)
            self.sbrickCommunications.connect('sbrick_disconnected_ok', self.on_sbrick_disconnected_ok)
            self.sbrickCommunications.connect('sbrick_channel_stop', self.on_sbrick_channel_stop)

            self.sbrickCommunications.connect_to_sbrick(self.password_owner)

        else:
            self.buttonConnect.set_label("Disconnecting...")
            self.sbrickCommunications.disconnect()
            self.set_child_communications(None)

    # noinspection PyUnusedLocal
    def on_button_estop_clicked(self, widget):
        if self.sbrickCommunications is not None:
            self.sbrickCommunications.stop_all()

    def set_child_communications(self, sbrick):
        self.sbrickCommunications = sbrick
        for widget in self.currentSBrickChannels:
            widget.set_sbrick(sbrick)
        self.SBrickInfoBox.set_sbrick(sbrick)
        self.SBrickFunctionsBox.set_sbrick(sbrick)
        self.SBrickSequenceBox.set_sbrick(sbrick)

    def write_configuration(self):
        self.SBrickFunctionsBox.write_configuration()
        self.SBrickSequenceBox.write_configuration()

    def on_sbrick_connected(self, sbrick):
        self.set_child_communications(sbrick)
        self.buttonConnect.set_label("Disconnect")
        self.buttonConnect.set_sensitive(True)
        self.buttonEStop.set_sensitive(True)
        self.buttonSettings.set_sensitive(False)
        # for act in self.actions_connected:
        #     act.set_enabled(True)

    # noinspection PyUnusedLocal
    def on_sbrick_disconnected_ok(self, sbrick):
        self.set_child_communications(None)
        self.buttonConnect.set_label("Connect")
        self.buttonConnect.set_sensitive(True)
        self.buttonEStop.set_sensitive(False)
        self.buttonSettings.set_sensitive(True)

        # for act in self.actions_connected:
        #     act.set_enabled(False)

    def on_sbrick_disconnected_error(self, sbrick, message):
        self.set_child_communications(None)
        self.buttonConnect.set_label("Connect")
        self.buttonConnect.set_sensitive(True)
        self.buttonEStop.set_sensitive(False)
        self.buttonSettings.set_sensitive(True)

        self.emit("show_message", sbrick.sBrickAddr, message, "SBrick has disconnected")
        self.set_child_communications(None)

    # noinspection PyUnusedLocal
    def on_sbrick_channel_stop(self, sbrick, channel):
        self.currentSBrickChannels[channel].stopped()

    def show_channels(self):
        children = self.channelBox.get_children()
        for child in children:
            self.channelBox.remove(child)

        for channelNumber in range(4):
            channel_box = None
            sb = self.sbrickConfiguration["channelConfiguration"][channelNumber]
            cc = sb["type"]
            if cc == 'motor':
                channel_box = SBrickMotorChannelBox(channelNumber, sb)
            elif cc == 'servo':
                channel_box = SBrickServoChannelBox(channelNumber, sb)
            self.channelBox.pack_start(channel_box, False, False, 0)
            self.currentSBrickChannels.append(channel_box)

        self.channelBox.show_all()


GObject.type_register(SBrickBox)
GObject.signal_new("sbrick_connected", SBrickBox, GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE, ())
GObject.signal_new("sbrick_disconnected", SBrickBox, GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE, ())
GObject.signal_new("show_message", SBrickBox, GObject.SignalFlags.RUN_LAST,
                   GObject.TYPE_NONE, [GObject.TYPE_STRING,
                                       GObject.TYPE_STRING,
                                       GObject.TYPE_STRING])

import gi
import sys

from PasswordDialog import PasswordDialog
from SBrickInfoBox import SBrickInfoBox
from SBrickMotorChannelBox import SBrickMotorChannelBox
from SBrickCommunications import SBrickCommunications
from SBrickServoChannelBox import SBrickServoChannelBox

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk, GLib, Gio

class SBrickBox(Gtk.Box):
    def __init__(self, sbrickConfiguration):
        Gtk.Box.__init__(self,orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=10)
        self.sbrickConfiguration = sbrickConfiguration
        # self.set_margin_bottom(10)
        # self.set_margin_top(10)
        # self.set_margin_left(10)
        # self.set_margin_right(10)

        self.topBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, margin=5)

        self.pack_start(self.topBox, False, True, 0)

        self.topBox.pack_start(Gtk.Label("SBrick: %s" % self.sbrickConfiguration["name"]), False, True, 0)
        self.topBox.pack_start(Gtk.Label("Address: %s" % self.sbrickConfiguration["addr"]), True, False, 0)

        self.buttonConnect = Gtk.Button.new_with_label("Connect")
        #self.buttonConnect.set_sensitive(False)
        self.buttonConnect.connect("clicked", self.on_button_connect_clicked)
        self.topBox.pack_start(self.buttonConnect, False, True, 0)

        self.SBrickInfoBox = SBrickInfoBox()
        self.pack_start(self.SBrickInfoBox, True, True, 0)
        self.password_guest = None
        self.password_owner = None
        self.currentSBrickChannels = []
        self.sbrickCommunications = None

        if "ownerPassword" in self.sbrickConfiguration:
            self.password_owner = self.sbrickConfiguration["ownerPassword"]
        if "guestPassword" in self.sbrickConfiguration:
            self.password_guest = self.sbrickConfiguration["guestPassword"]

        for channelNumber in range(4):
            channel_box = None
            sb = self.sbrickConfiguration["channelConfiguration"][channelNumber]
            cc = sb["type"]
            if cc == 'motor':
                channel_box = SBrickMotorChannelBox(channelNumber, sb)
            elif cc == 'servo':
                channel_box = SBrickServoChannelBox(channelNumber, sb)
            self.pack_start(channel_box, False, True, 0)
            self.currentSBrickChannels.append(channel_box)

        self.show_all()

    def disconnect(self):
        if self.sbrickCommunications:
            self.sbrickCommunications.disconnect()


    def on_button_connect_clicked(self,widget):
        self.buttonConnect.set_sensitive(False)
        if self.sbrickCommunications is None:
            self.buttonConnect.set_label("Connecting...")
            self.sbrickCommunications = SBrickCommunications(self.sbrickConfiguration["addr"])
            self.sbrickCommunications.connect_to_sbrick()

            if self.sbrickCommunications.need_authentication:
                if self.password_owner != None:
                    self.sbrickCommunications.authenticate_owner(self.password_owner)

            self.sbrickCommunications.start()
            self.sbrickCommunications.connect('sbrick_connected', self.on_sbrick_connected)
            self.sbrickCommunications.connect('sbrick_disconnected_error', self.on_sbrick_disconnected_error)
            self.sbrickCommunications.connect('sbrick_disconnected_ok', self.on_sbrick_disconnected_ok)
            self.sbrickCommunications.connect('sbrick_channel_stop', self.on_sbrick_channel_stop)

        else:
            self.buttonConnect.set_label("Disconnecting...")
            for widget in self.currentSBrickChannels:
                widget.set_sbrick(None)
            self.SBrickInfoBox.set_sbrick(None)
            self.sbrickCommunications.disconnect()

    def on_sbrick_connected(self, sbrick):
        self.SBrickInfoBox.set_sbrick(sbrick)
        for widget in self.currentSBrickChannels:
            widget.set_sbrick(sbrick)
        self.buttonConnect.set_label("Disconnect")
        self.buttonConnect.set_sensitive(True)
        # for act in self.actions_connected:
        #     act.set_enabled(True)

    def on_sbrick_disconnected_ok(self, sbrick):
        self.sbrickCommunications = None
        self.SBrickInfoBox.set_sbrick(None)
        for widget in self.currentSBrickChannels:
            widget.set_sbrick(None)
        self.buttonConnect.set_label("Connect")
        self.buttonConnect.set_sensitive(True)

        # for act in self.actions_connected:
        #     act.set_enabled(False)

    def on_sbrick_disconnected_error(self, sbrick, message):
        self.sbrickCommunications = None
        self.SBrickInfoBox.set_sbrick(None)
        for widget in self.currentSBrickChannels:
            widget.set_sbrick(None)
        messagedialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                          Gtk.ButtonsType.OK,
                                          "SBrick has disconnected")
        messagedialog.format_secondary_text(message)
        messagedialog.run()
        messagedialog.destroy()
        self.comboSBrick.set_sensitive(True)
        self.buttonConnect.set_label("Connect")
        self.buttonConnect.set_sensitive(True)
        # for act in self.actions_connected:
        #     act.set_enabled(False)

    def on_sbrick_channel_stop(self, sbrick, channel):
        self.currentSBrickChannels[channel].stopped()



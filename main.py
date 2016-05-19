#!/usr/bin/env python3
import gi
from SBrickInfoBox import SBrickInfoBox
from SBrickMotorChannelBox import SBrickMotorChannelBox
from SBrickCommunications import SBrickCommunications
from SBrickServoChannelBox import SBrickServoChannelBox
import simplejson as json

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="SBrick Controller")
        self.SBRICK_FW_VS = 0.0
        self.set_default_size(800, 480)
        self.connect("delete-event", self.on_delete_window)

        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.mainBox.set_margin_bottom(10)
        self.mainBox.set_margin_top(10)
        self.mainBox.set_margin_left(10)
        self.mainBox.set_margin_right(10)
        self.add(self.mainBox)

        self.sbrickBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.mainBox.pack_start(self.sbrickBox, False, True, 0)

        self.sbrickBox.pack_start(Gtk.Label("SBricks: "), False, True, 0)

        self.comboSBrick = Gtk.ComboBoxText()
        self.comboSBrick.set_entry_text_column(0)
        self.comboSBrick.connect("changed", self.on_combobox_sbricks_changed)

        self.sbrickBox.pack_start(self.comboSBrick, True, True, 0)
        self.config = None

        self.read_config()

        self.buttonConnect = Gtk.Button.new_with_label("Connect")
        self.buttonConnect.set_sensitive(False)
        self.buttonConnect.connect("clicked", self.on_button_connect_clicked)
        self.sbrickBox.pack_start(self.buttonConnect, False, True, 0)

        self.SBrickInfoBox = SBrickInfoBox()
        self.mainBox.pack_start(self.SBrickInfoBox, False, True, 0)

        self.currentSBrickChannels = []
        self.sbrickCommunications = None

    def on_delete_window(self, *args):
        if self.sbrickCommunications:
            self.sbrickCommunications.disconnect()
        Gtk.main_quit(*args)

        # def on_mainWindow_show(self, widget):
        #     print ("main window show")
        # self.devices = self.scanner.scan(10.0)

    def on_combobox_sbricks_changed(self, combo):
        text = combo.get_active_text()
        self.buttonConnect.set_sensitive(text is not None)

        for widget in self.currentSBrickChannels:
            self.mainBox.remove(widget)
        self.currentSBrickChannels = []

        if text is not None:
            sbrick = self.find_sbrick_config(text)
            for channelNumber in range(4):
                channel_box = None
                cc = sbrick["channelConfiguration"][channelNumber]
                if cc == 'motor':
                    channel_box = SBrickMotorChannelBox(channelNumber)
                elif cc == 'servo':
                    channel_box = SBrickServoChannelBox(channelNumber)
                self.mainBox.pack_start(channel_box, False, True, 0)
                self.currentSBrickChannels.append(channel_box)
            self.mainBox.show_all()

    def find_sbrick_config(self, combo_string):
        for sbrick in self.config:
            strn = "%s (%s)" % (sbrick["name"], sbrick["addr"])
            if strn == combo_string:
                return sbrick
        return None

    def on_button_connect_clicked(self, checkbutton):
        self.buttonConnect.set_sensitive(False)
        self.comboSBrick.set_sensitive(False)
        if self.sbrickCommunications is None:
            self.buttonConnect.set_label("Connecting...")
            sbrick = self.find_sbrick_config(self.comboSBrick.get_active_text())
            self.sbrickCommunications = SBrickCommunications(sbrick["addr"])
            self.sbrickCommunications.connect_to_sbrick()

            if self.sbrickCommunications.need_authentication:
                pass

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
        self.comboSBrick.set_sensitive(False)
        self.SBrickInfoBox.set_sbrick(sbrick)
        for widget in self.currentSBrickChannels:
            widget.set_sbrick(sbrick)
        self.buttonConnect.set_label("Disconnect")
        self.buttonConnect.set_sensitive(True)

    def on_sbrick_disconnected_ok(self, sbrick):
        self.sbrickCommunications = None
        self.SBrickInfoBox.set_sbrick(None)
        for widget in self.currentSBrickChannels:
            widget.set_sbrick(None)
        self.comboSBrick.set_sensitive(True)
        self.buttonConnect.set_label("Connect")
        self.buttonConnect.set_sensitive(True)

    def on_sbrick_disconnected_error(self, sbrick, message):
        self.sbrickCommunications = None
        self.comboSBrick.set_sensitive(False)
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

    def on_sbrick_channel_stop(self, sbrick, channel):
        self.currentSBrickChannels[channel].stopped()

    def read_config(self):
        fp = open("sbricks.json")
        try:
            self.config = json.load(fp)
        finally:
            self.close()
        for sbrick in self.config:
            self.comboSBrick.append_text("%s (%s)" % (sbrick["name"], sbrick["addr"]))


window = MainWindow()
window.show_all()
Gtk.main()

import gi
import sys

from PasswordDialog import PasswordDialog
from SBrickBox import SBrickBox
from SBrickInfoBox import SBrickInfoBox
from SBrickMotorChannelBox import SBrickMotorChannelBox
from SBrickCommunications import SBrickCommunications
from SBrickServoChannelBox import SBrickServoChannelBox
import simplejson as json

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk, GLib, Gio

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop("config",None)

        super().__init__(*args, **kwargs)
        self.set_default_size(800, 480)
        self.connect("delete-event", self.on_delete_window)

        # self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        # self.mainBox.set_margin_bottom(10)
        # self.mainBox.set_margin_top(10)
        # self.mainBox.set_margin_left(10)
        # self.mainBox.set_margin_right(10)
        # self.add(self.mainBox)

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        if self.config != None:
            for sbrick in self.config:
                page = SBrickBox(sbrick)
                self.notebook.append_page(page, Gtk.Label(sbrick["name"]))


        # self.sbrickBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        # self.mainBox.pack_start(self.sbrickBox, False, True, 0)
        #
        # self.sbrickBox.pack_start(Gtk.Label("SBricks: "), False, True, 0)
        #
        # self.comboSBrick = Gtk.ComboBoxText()
        # self.comboSBrick.set_entry_text_column(0)
        # self.comboSBrick.connect("changed", self.on_combobox_sbricks_changed)
        #
        # self.sbrickBox.pack_start(self.comboSBrick, True, True, 0)
        #
        #
        # self.buttonConnect = Gtk.Button.new_with_label("Connect")
        # self.buttonConnect.set_sensitive(False)
        # self.buttonConnect.connect("clicked", self.on_button_connect_clicked)
        # self.sbrickBox.pack_start(self.buttonConnect, False, True, 0)
        #
        # self.SBrickInfoBox = SBrickInfoBox()
        # self.mainBox.pack_start(self.SBrickInfoBox, False, True, 0)
        #
        # self.password_guest = None
        # self.password_owner = None
        # if self.config != None:
        #     for sbrick in self.config:
        #         self.comboSBrick.append_text("%s (%s)" % (sbrick["name"], sbrick["addr"]))

        # self.currentSBrickChannels = []
        # self.sbrickCommunications = None
        self.actions = []
        self.actions_connected = []

        self.setup_actions()
        self.show_all()

    def setup_actions(self):
        action = Gio.SimpleAction.new("set_owner_password", None)
        action.connect("activate", self.on_set_owner_password)
        self.add_action(action)
        self.actions.append(action)

        action = Gio.SimpleAction.new("set_guest_password", None)
        action.connect("activate", self.on_set_guest_password)
        self.add_action(action)
        self.actions.append(action)

        action = Gio.SimpleAction.new("write_owner_password", None)
        action.connect("activate", self.on_write_owner_password)
        self.add_action(action)
        self.actions.append(action)
        self.actions_connected.append(action)

        action = Gio.SimpleAction.new("write_guest_password", None)
        action.connect("activate", self.on_write_guest_password)
        self.add_action(action)
        self.actions.append(action)
        self.actions_connected.append(action)

        action = Gio.SimpleAction.new("clear_owner_password", None)
        action.connect("activate", self.on_clear_owner_password)
        self.add_action(action)
        self.actions.append(action)
        self.actions_connected.append(action)

        action = Gio.SimpleAction.new("clear_guest_password", None)
        action.connect("activate", self.on_clear_guest_password)
        self.add_action(action)
        self.actions.append(action)
        self.actions_connected.append(action)

        for act in self.actions_connected:
            act.set_enabled(False)

        # action.connect('activate')

    def on_delete_window(self, *args):
        for ch in self.notebook.get_children():
            ch.disconnect()
        Gtk.main_quit(*args)

        # def on_mainWindow_show(self, widget):
        #     print ("main window show")
        # self.devices = self.scanner.scan(10.0)

    # def on_combobox_sbricks_changed(self, combo):
    #     text = combo.get_active_text()
    #     self.buttonConnect.set_sensitive(text is not None)
    #
    #     for widget in self.currentSBrickChannels:
    #         self.mainBox.remove(widget)
    #     self.currentSBrickChannels = []
    #
    #     if text is not None:
    #         sbrick = self.find_sbrick_config(text)
    #         if "ownerPassword" in sbrick:
    #             self.password_owner = sbrick["ownerPassword"]
    #         if "guestPassword" in sbrick:
    #             self.password_guest = sbrick["guestPassword"]
    #
    #         for channelNumber in range(4):
    #             channel_box = None
    #             sb = sbrick["channelConfiguration"][channelNumber]
    #             cc = sb["type"]
    #             if cc == 'motor':
    #                 channel_box = SBrickMotorChannelBox(channelNumber, sb)
    #             elif cc == 'servo':
    #                 channel_box = SBrickServoChannelBox(channelNumber,sb)
    #             self.mainBox.pack_start(channel_box, False, True, 0)
    #             self.currentSBrickChannels.append(channel_box)
    #         self.mainBox.show_all()

    # def find_sbrick_config(self, combo_string):
    #     for sbrick in self.config:
    #         strn = "%s (%s)" % (sbrick["name"], sbrick["addr"])
    #         if strn == combo_string:
    #             return sbrick
    #     return None

    # def on_button_connect_clicked(self, checkbutton):
    #     self.buttonConnect.set_sensitive(False)
    #     self.comboSBrick.set_sensitive(False)
    #     if self.sbrickCommunications is None:
    #         self.buttonConnect.set_label("Connecting...")
    #         sbrick = self.find_sbrick_config(self.comboSBrick.get_active_text())
    #         self.sbrickCommunications = SBrickCommunications(sbrick["addr"])
    #         self.sbrickCommunications.connect_to_sbrick()
    #
    #         if self.sbrickCommunications.need_authentication:
    #             if self.password_owner != None:
    #                 self.sbrickCommunications.authenticate_owner(self.password_owner)
    #
    #         self.sbrickCommunications.start()
    #         self.sbrickCommunications.connect('sbrick_connected', self.on_sbrick_connected)
    #         self.sbrickCommunications.connect('sbrick_disconnected_error', self.on_sbrick_disconnected_error)
    #         self.sbrickCommunications.connect('sbrick_disconnected_ok', self.on_sbrick_disconnected_ok)
    #         self.sbrickCommunications.connect('sbrick_channel_stop', self.on_sbrick_channel_stop)
    #
    #
    #     else:
    #         self.buttonConnect.set_label("Disconnecting...")
    #         for widget in self.currentSBrickChannels:
    #             widget.set_sbrick(None)
    #         self.SBrickInfoBox.set_sbrick(None)
    #         self.sbrickCommunications.disconnect()
    #
    # def on_sbrick_connected(self, sbrick):
    #     self.comboSBrick.set_sensitive(False)
    #     self.SBrickInfoBox.set_sbrick(sbrick)
    #     for widget in self.currentSBrickChannels:
    #         widget.set_sbrick(sbrick)
    #     self.buttonConnect.set_label("Disconnect")
    #     self.buttonConnect.set_sensitive(True)
    #     for act in self.actions_connected:
    #         act.set_enabled(True)
    #
    # def on_sbrick_disconnected_ok(self, sbrick):
    #     self.sbrickCommunications = None
    #     self.SBrickInfoBox.set_sbrick(None)
    #     for widget in self.currentSBrickChannels:
    #         widget.set_sbrick(None)
    #     self.comboSBrick.set_sensitive(True)
    #     self.buttonConnect.set_label("Connect")
    #     self.buttonConnect.set_sensitive(True)
    #
    #     for act in self.actions_connected:
    #         act.set_enabled(False)
    #
    # def on_sbrick_disconnected_error(self, sbrick, message):
    #     self.sbrickCommunications = None
    #     self.comboSBrick.set_sensitive(False)
    #     self.SBrickInfoBox.set_sbrick(None)
    #     for widget in self.currentSBrickChannels:
    #         widget.set_sbrick(None)
    #     messagedialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
    #                                       Gtk.ButtonsType.OK,
    #                                       "SBrick has disconnected")
    #     messagedialog.format_secondary_text(message)
    #     messagedialog.run()
    #     messagedialog.destroy()
    #     self.comboSBrick.set_sensitive(True)
    #     self.buttonConnect.set_label("Connect")
    #     self.buttonConnect.set_sensitive(True)
    #     for act in self.actions_connected:
    #         act.set_enabled(False)
    #
    # def on_sbrick_channel_stop(self, sbrick, channel):
    #     self.currentSBrickChannels[channel].stopped()


    def on_set_owner_password(self, action, param):
        dialog = PasswordDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.password_owner = dialog.get_password()
        dialog.destroy()


    def on_set_guest_password(self, action, param):
        dialog = PasswordDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.password_guest = dialog.get_password()
        dialog.destroy()


    def on_write_owner_password(self, action, param):
        if self.sbrickCommunications != None:
            if self.password_owner != "":
                self.sbrickCommunications.set_owner_password(self.password_owner)


    def on_write_guest_password(self, action, param):
        if self.sbrickCommunications != None:
            if self.password_owner != "":
                self.sbrickCommunications.set_owner_password(self.password_guest)


    def on_clear_owner_password(self, action, param):
        if self.sbrickCommunications != None:
            self.sbrickCommunications.clear_owner_password()

    def on_clear_guest_password(self, action, param):
        if self.sbrickCommunications != None:
            self.sbrickCommunications.clear_guest_password()

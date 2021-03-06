import gi

from PasswordDialog import PasswordDialog
from SBrickBox import SBrickBox
from SBrickConfigureDialog import SBrickConfigureDialog
from SequencesBox import SequencesBox
from ObservingDict import ObservingDict

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk, GLib, Gio


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop("config", None)
        self.sbrick_communications_store = ObservingDict(dict())

        Gtk.ApplicationWindow.__init__(self, *args, **kwargs)

        # self.set_default_size(800, 480)
        self.resize(800, 480)
        self.connect("delete-event", self.on_delete_window)

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)
        self.notebook.set_scrollable(True)

        if self.config is not None:
            for sbrick in self.config:
                page = SBrickBox(sbrick, self.sbrick_communications_store)
                page.connect("show_message", self.on_show_message)
                self.notebook.append_page(page, Gtk.Label(sbrick["name"]))

        self.sequences_box = SequencesBox(self.config, self.sbrick_communications_store)
        self.notebook.append_page(self.sequences_box, Gtk.Label("Sequences"))

        self.actions = []
        self.actions_connected = []

        self.setup_actions()
        self.show_all()

        # noinspection PyUnusedLocal


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

        action = Gio.SimpleAction.new_stateful("toggle_fullscreen", None, GLib.Variant.new_boolean(False))
        action.connect("change-state", self.on_toggle_fullscreen)
        self.add_action(action)

        action = Gio.SimpleAction.new("show_size", None)
        action.connect("activate", self.on_show_size)
        self.add_action(action)

        action = Gio.SimpleAction.new("add_sbrick", None)
        action.connect("activate", self.on_add_sbrick)
        self.add_action(action)

        action = Gio.SimpleAction.new("delete_sbrick", None)
        action.connect("activate", self.on_delete_sbrick)
        self.add_action(action)

        for act in self.actions_connected:
            act.set_enabled(False)

    def get_showing_sbrick_box(self):
        idx = self.notebook.get_current_page()
        return self.notebook.get_nth_page(idx)

    def on_delete_window(self, *args):
        for ch in self.notebook.get_children():
            ch.disconnect_sbrick()
        Gtk.main_quit(*args)

    def on_add_sbrick(self, action, param):
        sc = dict()
        dialog = SBrickConfigureDialog(self, sc)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.config.append(sc)
            self.add_sbrick(sc)

        dialog.destroy()

        # noinspection PyUnusedLocal

    def on_delete_sbrick(self, action, param):
        pass

    def add_sbrick(self, config):
        page = SBrickBox(config)
        page.connect("show_message", self.on_show_message)
        self.notebook.append_page(page, Gtk.Label(config["name"]))

    # noinspection PyUnusedLocal,PyUnusedLocal
    def on_set_owner_password(self, action, param):
        dialog = PasswordDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.get_showing_sbrick_box().set_password_owner(dialog.get_password())
        dialog.destroy()

    # noinspection PyUnusedLocal,PyUnusedLocal
    def on_set_guest_password(self, action, param):
        dialog = PasswordDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.get_showing_sbrick_box().set_password_guest(dialog.get_password())
        dialog.destroy()

    # noinspection PyUnusedLocal,PyUnusedLocal
    def on_write_owner_password(self, action, param):
        self.get_showing_sbrick_box().write_owner_password()

    # noinspection PyUnusedLocal,PyUnusedLocal
    def on_write_guest_password(self, action, param):
        self.get_showing_sbrick_box().write_guest_password()

    # noinspection PyUnusedLocal,PyUnusedLocal
    def on_clear_owner_password(self, action, param):
        self.get_showing_sbrick_box().clear_owner_password()

    # noinspection PyUnusedLocal,PyUnusedLocal
    def on_clear_guest_password(self, action, param):
        self.get_showing_sbrick_box().clear_guest_password()

    def show_message(self, title, message, mainmessage):
        messagedialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                          Gtk.ButtonsType.OK,
                                          "[%s] %s" % (title, mainmessage))
        messagedialog.format_secondary_text(message)
        messagedialog.run()
        messagedialog.destroy()

    # noinspection PyUnusedLocal
    def on_show_message(self, widget, title, message, mainmessage):
        self.show_message(title, message, mainmessage)

    def on_toggle_fullscreen(self, action, value):
        action.set_state(value)
        if value.get_boolean():
            self.fullscreen()
        else:
            self.unfullscreen()

    # noinspection PyUnusedLocal,PyUnusedLocal
    def on_show_size(self, action, param):
        print("%d %d" % (self.get_allocated_width(), self.get_allocated_height()))

    def write_configuration(self):
        for page in self.notebook.get_children():
            page.write_configuration()

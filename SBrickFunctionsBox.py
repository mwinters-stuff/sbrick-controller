import gi

from FunctionConfigureDialog import FunctionConfigureDialog

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk, GLib, Gio, GObject

class FunctionGroupBox(Gtk.Frame):
    def __init__(self, configuration, channels):
        Gtk.Frame.__init__(self)
        self.configuration = configuration
        self.channels = channels

        if "group" in configuration:
            self.set_label(configuration["group"])

        hbox = Gtk.Box(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox.set_homogeneous(False)
        self.add(hbox)

        self.button_settings = Gtk.Button.new()
        self.button_settings.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_PREFERENCES, Gtk.IconSize.BUTTON))
        self.button_settings.connect("clicked", self.on_settings_clicked)
        hbox.pack_start(self.button_settings, False, True, 0)

        self.hbox = Gtk.Box(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox.pack_start(self.hbox, True, True, 0)

        if "functions" in configuration:
            for func in configuration["functions"]:
                button = Gtk.Button(func["label"])
                button.connect("clicked", self.on_button_clicked)
                button.brick_function = func
                self.hbox.pack_start(button, True, True, 0)

        self.sbrick = None
        self.hbox.set_sensitive(False)

    def on_button_clicked(self, widget):
        function = widget.brick_function
        print("button function",function)

        channelName = function["channel"]
        time = -1
        if "time" in function:
            time = int(function["time"])
        pwm = 0
        if "pwm" in function:
            pwm = int(function["pwm"])
        reverse = False
        if "reverse" in function:
            reverse = function["reverse"] == "true"
        off = None
        if "off" in function:
            off = function["off"]

        if pwm > 0:
            # drive
            self.sbrick.drive(channelName,pwm,reverse,time,off == "brake")
        else:
            # stop
            pwm = 0
            self.sbrick.stop(channelName,off == "brake")

    def do_add_new(self):
        return self.do_settings()

    def on_settings_clicked(self, widget):
        self.do_settings()

    def do_settings(self):
        dialog = FunctionConfigureDialog(self.get_toplevel(), self.configuration, self.channels)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            ch = self.hbox.get_children()
            for c in ch:
                self.hbox.remove(c)
                c.destroy()
            for func in self.configuration["functions"]:
                button = Gtk.Button(func["label"])
                button.connect("clicked", self.on_button_clicked)
                button.brick_function = func
                self.hbox.pack_start(button, True, True, 0)
            self.hbox.show_all()
            dialog.destroy()
            return True
        else:
            dialog.destroy()
            return False



    def set_sbrick(self, sbrick):
        self.sbrick = sbrick
        # self.button_settings.set_sensitive(sbrick is None)
        self.hbox.set_sensitive(sbrick is not None)


class SBrickFunctionsBox(Gtk.ListBox):
    def __init__(self, configuration, channels):
        Gtk.ListBox.__init__(self)

        self.configuration = configuration
        self.channels = channels
        self.sbrick = None
        self.functionGroups = []

        self.action_box = Gtk.Box(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.action_box.set_homogeneous(False)
        self.add(self.action_box)
        self.get_row_at_index(0).set_activatable(False)
        self.get_row_at_index(0).set_selectable(False)
        # self.pack_start(self.action_box, False, True, 0)

        self.button_add = Gtk.Button.new()
        self.button_add.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON))
        self.button_add.connect("clicked", self.on_add_clicked)
        self.action_box.pack_start(self.button_add, False, True, 0)

        self.button_del = Gtk.Button.new()
        self.button_del.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_DELETE, Gtk.IconSize.BUTTON))
        self.button_del.connect("clicked", self.on_delete_clicked)
        self.action_box.pack_start(self.button_del, False, True, 0)

        for group in configuration:
            fg = FunctionGroupBox(group, channels)
            # self.pack_start(fg, False, True, 0)
            self.add(fg)
            self.functionGroups.append(fg)

    def set_sbrick(self, sbrick):
        self.sbrick = sbrick
        for fg in self.functionGroups:
            fg.set_sbrick(sbrick)

    def on_add_clicked(self, widget):
        group = dict()
        fg = FunctionGroupBox(group, self.channels)
        self.add(fg)
        if fg.do_add_new():
            fg.set_sbrick(self.sbrick)
            self.functionGroups.append(fg)
            self.configuration.append(group)
            self.show_all()
        else:
            self.remove(fg)
            fg.destroy()

    def on_delete_clicked(self, widget):
        row = self.get_selected_row()
        ch = row.get_child()
        self.configuration.remove(ch.configuration)
        self.remove(row)

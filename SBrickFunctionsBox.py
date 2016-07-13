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

        vbox = Gtk.Box(self, orientation=Gtk.Orientation.VERTICAL, spacing=2)
        vbox.set_homogeneous(False)
        self.add(vbox)

        self.label = Gtk.Label()
        vbox.pack_start(self.label, False, True, 0)
        if "group" in configuration:
            self.label.set_text(configuration["group"])

        hbox = Gtk.Box(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox.set_homogeneous(False)
        vbox.pack_start(hbox, False, True, 0)

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
        print("button function", function)

        channelname = function["channel"]
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
            self.sbrick.drive(channelname, pwm, reverse, time, off == "brake")
        else:
            # stop
            self.sbrick.stop(channelname, off == "brake")

    def do_add_new(self):
        return self.do_settings()

    # noinspection PyUnusedLocal
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
            self.label.set_text(self.configuration["group"])
            self.show_all()
            dialog.destroy()
            return True
        else:
            dialog.destroy()
            return False

    def set_sbrick(self, sbrick):
        self.sbrick = sbrick
        # self.button_settings.set_sensitive(sbrick is None)
        self.hbox.set_sensitive(sbrick is not None)


class SBrickFunctionsBox(Gtk.Box):
    def __init__(self, configuration, channels):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.set_homogeneous(False)

        self.tool_bar = Gtk.Toolbar()
        self.pack_start(self.tool_bar, False, True, 0)

        tool = Gtk.ToolButton.new(Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON), "Add")
        tool.connect("clicked", self.on_add_clicked)
        self.tool_bar.insert(tool, -1)
        tool = Gtk.ToolButton.new(Gtk.Image.new_from_stock(Gtk.STOCK_DELETE, Gtk.IconSize.BUTTON), "Delete")
        tool.connect("clicked", self.on_delete_clicked)
        self.tool_bar.insert(tool, -1)
        self.content = Gtk.ListBox()

        self.scrollTree = Gtk.ScrolledWindow()
        self.scrollTree.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrollTree.add_with_viewport(self.content)
        self.scrollTree.set_min_content_height(100)
        self.pack_start(self.scrollTree, True, True, 0)

        self.configuration = configuration
        self.channels = channels
        self.sbrick = None
        self.functionGroups = []

        for group in configuration:
            fg = FunctionGroupBox(group, channels)
            # self.pack_start(fg, False, True, 0)
            self.content.add(fg)
            self.functionGroups.append(fg)

    def write_configuration(self):
        pass

    def set_sbrick(self, sbrick):
        self.sbrick = sbrick
        for fg in self.functionGroups:
            fg.set_sbrick(sbrick)

    # noinspection PyUnusedLocal
    def on_add_clicked(self, widget):
        group = dict()
        fg = FunctionGroupBox(group, self.channels)
        self.content.add(fg)
        if fg.do_add_new():
            fg.set_sbrick(self.sbrick)
            self.functionGroups.append(fg)
            self.configuration.append(group)
            self.show_all()
        else:
            self.content.remove(fg)
            fg.destroy()

    # noinspection PyUnusedLocal
    def on_delete_clicked(self, widget):
        row = self.content.get_selected_row()
        ch = row.get_child()
        self.configuration.remove(ch.configuration)
        self.content.remove(row)

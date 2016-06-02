import gi

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk, GLib, Gio, GObject

class FunctionGroupBox(Gtk.Frame):
    def __init__(self, configuration):
        Gtk.Frame.__init__(self)
        self.set_label(configuration["group"])

        self.hbox = Gtk.Box(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(self.hbox)

        for func in configuration["functions"]:
            button = Gtk.Button(func["label"])
            button.connect("clicked", self.on_button_clicked)
            button.brick_function = func
            self.hbox.pack_start(button, False, True, 0)

        self.sbrick = None
        self.set_sensitive(False)

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

    def set_sbrick(self, sbrick):
        self.sbrick = sbrick
        self.set_sensitive(sbrick is not None)


class SBrickFunctionsBox(Gtk.Box):
    def __init__(self, configuration):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=10)
        self.configuration = configuration
        self.sbrick = None
        self.functionGroups = []

        for group in configuration:
            fg = FunctionGroupBox(group)
            self.pack_start(fg, False, True, 0)
            self.functionGroups.append(fg)

    def set_sbrick(self, sbrick):
        self.sbrick = sbrick
        for fg in self.functionGroups:
            fg.set_sbrick(sbrick)




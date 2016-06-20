import gi

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk


class FunctionOptions(Gtk.FlowBox):
    def __init__(self, configuration, channels):
        Gtk.FlowBox.__init__(self)
        self.configuration = configuration

        self.set_max_children_per_line(5)
        self.set_min_children_per_line(5)
        self.set_selection_mode(Gtk.SelectionMode.NONE)

        self.channelStore = Gtk.ListStore(str, str)
        for channel in channels:
            self.channelStore.append([channel["id"], channel["name"]])

        self.add(Gtk.Label("Function Name:"))
        self.edit_name = Gtk.Entry()
        self.edit_name.set_max_length(20)
        self.add(self.edit_name)

        self.add(Gtk.Label("Channel:"))
        self.combo_channel = Gtk.ComboBoxText()
        self.combo_channel.set_id_column(0)
        self.combo_channel.set_model(self.channelStore)
        renderer_text = Gtk.CellRendererText()
        self.combo_channel.clear()
        self.combo_channel.pack_start(renderer_text, True)
        self.combo_channel.add_attribute(renderer_text, "text", 1)
        self.add(self.combo_channel)

        self.vbox = Gtk.FlowBox()  # , orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.vbox.set_border_width(2)
        self.vbox.set_max_children_per_line(7)
        self.vbox.set_min_children_per_line(7)
        self.vbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.add(self.vbox)

        self.vbox.add(Gtk.Label("PWM: "))
        self.pwmAdjustment = Gtk.Adjustment(255, 0, 255, 5, 10, 0.0)
        self.spinPWM = Gtk.SpinButton.new(self.pwmAdjustment, 5, 0)
        self.vbox.add(self.spinPWM)

        self.checkReverse = Gtk.CheckButton("Reverse")
        self.vbox.add(self.checkReverse)

        self.checkTime = Gtk.CheckButton("Time MS:")
        self.vbox.add(self.checkTime)
        self.checkTime.connect("toggled", self.on_time_toggled)

        self.timeAdjustment = Gtk.Adjustment(1000, -1, 10000, 10, 100, 0.0)
        self.spinTime = Gtk.SpinButton.new(self.timeAdjustment, 10, 0)
        self.vbox.add(self.spinTime)
        self.spinTime.set_sensitive(False)

        self.checkBrake = Gtk.CheckButton("Break Stop")
        self.vbox.add(self.checkBrake)

        if "channel" in self.configuration:
            self.edit_name.set_text(configuration["label"])
        if "label" in self.configuration:
            self.combo_channel.set_active_id(configuration["channel"])

        if "pwm" in configuration:
            self.pwmAdjustment.set_value(int(configuration["pwm"]))
        else:
            self.pwmAdjustment.set_value(0)

        if "reverse" in configuration:
            self.checkReverse.set_active(configuration["reverse"] == "true")

        if "time" in configuration:
            if int(configuration["time"]) > -1:
                self.checkTime.set_active(True)
                self.timeAdjustment.set_value(int(configuration["time"]))
            else:
                self.checkTime.set_active(False)

        if "off" in configuration:
            self.checkBrake.set_active(configuration["off"] == "brake")

    def on_time_toggled(self, checkbox):
        self.spinTime.set_sensitive(checkbox.get_active())

    def write_configuration(self):
        self.configuration["label"] = self.edit_name.get_text()
        self.configuration["channel"] = self.combo_channel.get_active_id()

        pwm = int(self.pwmAdjustment.get_value())
        if pwm > 0:
            self.configuration["pwm"] = pwm
            if self.checkReverse.get_active():
                self.configuration["reverse"] = "true"
            else:
                self.configuration["reverse"] = "false"
            if self.checkTime.get_active():
                self.configuration["time"] = int(self.timeAdjustment.get_value())
            else:
                self.configuration["time"] = -1

        else:
            if "pwm" in self.configuration:
                del self.configuration["pwm"]
            if "reverse" in self.configuration:
                del self.configuration["reverse"]
            if "time" in self.configuration:
                del self.configuration["time"]
        if self.checkBrake.get_active():
            self.configuration["off"] = "brake"
        else:
            self.configuration["off"] = "coast"


class FunctionConfigureDialog(Gtk.Dialog):
    def __init__(self, parent, configuration, channels):
        Gtk.Dialog.__init__(self, "Configure Function", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.configuration = configuration
        self.channels = channels
        self.set_default_size(600, 400)
        # self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.content = Gtk.FlowBox()
        self.content.set_max_children_per_line(1)
        self.content.set_min_children_per_line(1)
        self.get_content_area().add(self.content)

        # hbox = Gtk.FlowBox()
        self.action_box = Gtk.Box(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.action_box.set_homogeneous(False)
        self.content.add(self.action_box)

        self.action_box.pack_start(Gtk.Label("Group Name:"), False, True, 0)
        self.edit_name = Gtk.Entry()
        self.edit_name.set_max_length(20)
        self.action_box.pack_start(self.edit_name, False, True, 0)
        if "group" in configuration:
            self.edit_name.set_text(configuration["group"])

        self.button_add = Gtk.Button.new()
        self.button_add.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON))
        self.button_add.connect("clicked", self.on_add_clicked)
        self.action_box.pack_start(self.button_add, False, True, 0)

        self.button_del = Gtk.Button.new()
        self.button_del.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_DELETE, Gtk.IconSize.BUTTON))
        self.button_del.connect("clicked", self.on_delete_clicked)
        self.action_box.pack_start(self.button_del, False, True, 0)

        self.functions = []
        if "functions" in configuration:
            for func in configuration["functions"]:
                fo = FunctionOptions(func, channels)
                # self.content.pack_start(fo, False, True, 0)
                self.content.add(fo)
                self.functions.append(fo)
        else:
            configuration["functions"] = []

        self.show_all()
        self.connect('response', self.on_response)

    def on_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            self.configuration["group"] = self.edit_name.get_text()
            for func in self.functions:
                func.write_configuration()

    def on_add_clicked(self, widget):
        func = dict()
        self.configuration["functions"].append(func)
        fo = FunctionOptions(func, self.channels)
        self.content.add(fo)
        self.functions.append(fo)
        self.content.show_all()

    def on_delete_clicked(self, widget):
        widgets = self.content.get_selected_children()
        for widget in widgets:
            fo = widget.get_child()
            if fo != self.action_box:
                self.configuration["functions"].remove(fo.configuration)
                self.content.remove(widget)

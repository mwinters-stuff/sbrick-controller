import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class FunctionOptions(Gtk.Box):
    def __init__(self, configuration, channels):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=3, margin=2)
        self.set_homogeneous(False)
        self.configuration = configuration
        self.channels = channels

        self.channelStore = Gtk.ListStore(str, str)
        for channel in channels:
            self.channelStore.append([channel["id"], channel["name"]])

        self.pack_start(Gtk.Label("Function Name:"), False, True, 0)
        self.edit_name = Gtk.Entry()
        self.edit_name.set_max_length(10)
        self.pack_start(self.edit_name, False, True, 0)

        self.pack_start(Gtk.Label("Channel:"), False, True, 0)
        self.combo_channel = Gtk.ComboBoxText()
        self.combo_channel.set_id_column(0)
        self.combo_channel.set_model(self.channelStore)
        renderer_text = Gtk.CellRendererText()
        self.combo_channel.clear()
        self.combo_channel.pack_start(renderer_text, True)
        self.combo_channel.add_attribute(renderer_text, "text", 1)
        self.pack_start(self.combo_channel, False, True, 0)
        self.combo_channel.connect("changed", self.on_combo_channel_changed)

        # self.vbox = Gtk.FlowBox()  # , orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        # self.vbox.set_border_width(2)
        # self.vbox.set_max_children_per_line(7)
        # self.vbox.set_min_children_per_line(7)
        # self.vbox.set_selection_mode(Gtk.SelectionMode.NONE)
        # self.pack_start(self.vbox, False, True, 0)

        self.labelPwm = Gtk.Label("PWM: ")
        self.pack_start(self.labelPwm, False, True, 0)
        self.pwmAdjustment = Gtk.Adjustment(255, 0, 255, 5, 10, 0.0)
        self.spinPWM = Gtk.SpinButton.new(self.pwmAdjustment, 5, 0)
        self.pack_start(self.spinPWM, False, True, 0)

        self.checkReverse = Gtk.CheckButton("Reverse")
        self.pack_start(self.checkReverse, False, True, 0)

        self.labelPosition = Gtk.Label("Angle: ")
        self.pack_start(self.labelPosition, False, True, 0)

        self.pwmStore = Gtk.ListStore(str, str)
        self.pwmStore.append(["-255", "-90.0"])
        self.pwmStore.append(["-223", "-77.1"])
        self.pwmStore.append(["-190", "-64.3"])
        self.pwmStore.append(["-161", "-51.4"])
        self.pwmStore.append(["-126", "-38.6"])
        self.pwmStore.append(["-97", "-25.7"])
        self.pwmStore.append(["-67", "-12.9"])
        self.pwmStore.append(["0", "0.00"])
        self.pwmStore.append(["67", "12.9"])
        self.pwmStore.append(["97", "25.7"])
        self.pwmStore.append(["126", "38.6"])
        self.pwmStore.append(["161", "51.4"])
        self.pwmStore.append(["190", "64.3"])
        self.pwmStore.append(["223", "77.1"])
        self.pwmStore.append(["255", "90.0"])

        self.comboPosition = Gtk.ComboBoxText()
        self.comboPosition.set_id_column(0)
        self.comboPosition.set_model(self.pwmStore)
        renderer_text = Gtk.CellRendererText()
        self.comboPosition.clear()
        self.comboPosition.pack_start(renderer_text, True)
        self.comboPosition.add_attribute(renderer_text, "text", 1)
        self.comboPosition.set_active_id("0")
        self.pack_start(self.comboPosition, False, True, 0)


        self.checkTime = Gtk.CheckButton("Time MS:")
        self.pack_start(self.checkTime, False, True, 0)
        self.checkTime.connect("toggled", self.on_time_toggled)

        self.timeAdjustment = Gtk.Adjustment(1000, -1, 30000, 100, 1000, 0.0)
        self.spinTime = Gtk.SpinButton.new(self.timeAdjustment, 10, 0)
        self.pack_start(self.spinTime, False, True, 0)
        self.spinTime.set_sensitive(False)

        self.checkBrake = Gtk.CheckButton("Break Stop")
        self.pack_start(self.checkBrake, False, True, 0)

        if "channel" in self.configuration:
            self.edit_name.set_text(configuration["label"])
        if "label" in self.configuration:
            self.combo_channel.set_active_id(configuration["channel"])

        if "pwm" in configuration:
            self.pwmAdjustment.set_value(int(configuration["pwm"]))
            self.comboPosition.set_active_id(str(configuration["pwm"]))
        else:
            self.pwmAdjustment.set_value(0)

        if "reverse" in configuration:
            self.checkReverse.set_active(configuration["reverse"] == "true")
            self.comboPosition.set_active_id("-%s" % self.comboPosition.get_active_id())

        if "time" in configuration:
            if int(configuration["time"]) > -1:
                self.checkTime.set_active(True)
                self.timeAdjustment.set_value(int(configuration["time"]))
            else:
                self.checkTime.set_active(False)

        if "off" in configuration:
            self.checkBrake.set_active(configuration["off"] == "brake")
        self.change_widget_visibility()

    def change_widget_visibility(self):
        chann = self.combo_channel.get_active_id()
        for channel in self.channels:
            if chann == channel["id"]:
                motor = channel["type"] == "motor"
                self.comboPosition.set_visible(not motor)
                self.labelPosition.set_visible(not motor)
                self.labelPwm.set_visible(motor)
                self.spinPWM.set_visible(motor)
                self.checkReverse.set_visible(motor)
                self.checkBrake.set_visible(motor)

    def on_time_toggled(self, checkbox):
        self.spinTime.set_sensitive(checkbox.get_active())

    def write_configuration(self):
        self.configuration["label"] = self.edit_name.get_text()
        self.configuration["channel"] = self.combo_channel.get_active_id()

        if self.spinPWM.is_visible():
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
        else:
            pwm = int(self.comboPosition.get_active_id())
            self.configuration["reverse"] = "false"
            if pwm < 0:
                pwm = abs(pwm)
                self.configuration["reverse"] = "true"

            if pwm > 0:
                if self.checkTime.get_active():
                    self.configuration["time"] = int(self.timeAdjustment.get_value())
                else:
                    self.configuration["time"] = -1
            else:
                if "time" in self.configuration:
                    del self.configuration["time"]
            self.configuration["off"] = "coast"
            self.configuration["pwm"] = pwm

    def on_combo_channel_changed(self, widget):
        self.change_widget_visibility()


class FunctionConfigureDialog(Gtk.Dialog):
    def __init__(self, parent, configuration, channels):
        Gtk.Dialog.__init__(self, "Configure Function", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.configuration = configuration
        self.channels = channels
        self.set_default_size(600, 400)

        self.tool_bar = Gtk.Toolbar()
        self.get_content_area().pack_start(self.tool_bar, False, True, 0)

        self.tool_add = Gtk.ToolButton.new(Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON), "Add")
        self.tool_add.connect("clicked", self.on_add_clicked)
        self.tool_bar.insert(self.tool_add, -1)

        self.tool_delete = Gtk.ToolButton.new(Gtk.Image.new_from_stock(Gtk.STOCK_DELETE, Gtk.IconSize.BUTTON), "Delete")
        self.tool_delete.connect("clicked", self.on_delete_clicked)
        self.tool_bar.insert(self.tool_delete, -1)

        self.tool_bar.insert(Gtk.SeparatorToolItem.new(), -1)

        self.tool_up = Gtk.ToolButton.new(Gtk.Image.new_from_stock(Gtk.STOCK_GO_UP, Gtk.IconSize.BUTTON), "Add")
        self.tool_up.connect("clicked", self.on_up_clicked)
        self.tool_bar.insert(self.tool_up, -1)

        self.tool_down = Gtk.ToolButton.new(Gtk.Image.new_from_stock(Gtk.STOCK_GO_DOWN, Gtk.IconSize.BUTTON), "Add")
        self.tool_down.connect("clicked", self.on_down_clicked)
        self.tool_bar.insert(self.tool_down, -1)

        self.group_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.group_box.set_homogeneous(False)
        self.get_content_area().pack_start(self.group_box, False, True, 0)

        self.group_box.pack_start(Gtk.Label("Group Name:"), False, True, 0)
        self.edit_name = Gtk.Entry()
        self.edit_name.set_max_length(20)
        self.group_box.pack_start(self.edit_name, False, True, 0)
        if "group" in configuration:
            self.edit_name.set_text(configuration["group"])

        self.list_content = Gtk.ListBox()
        self.scrollTree = Gtk.ScrolledWindow()
        self.scrollTree.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrollTree.add_with_viewport(self.list_content)
        self.scrollTree.set_min_content_height(100)
        self.get_content_area().pack_start(self.scrollTree, True, True, 0)

        self.functions = []
        if "functions" in configuration:
            for func in configuration["functions"]:
                fo = FunctionOptions(func, channels)
                self.list_content.add(fo)
                self.functions.append(fo)
        else:
            configuration["functions"] = []

        self.show_all()
        self.connect('response', self.on_response)
        for widget in self.functions:
            widget.change_widget_visibility()

    # noinspection PyUnusedLocal
    def on_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            self.configuration["group"] = self.edit_name.get_text()
            for func in self.functions:
                func.write_configuration()

    # noinspection PyUnusedLocal
    def on_add_clicked(self, widget):
        func = dict()
        self.configuration["functions"].append(func)
        fo = FunctionOptions(func, self.channels)
        self.list_content.add(fo)
        self.functions.append(fo)
        self.list_content.show_all()

    # noinspection PyUnusedLocal
    def on_delete_clicked(self, widget):
        row = self.list_content.get_selected_row()
        if row is not None:
            fo = row.get_child()
            self.configuration["functions"].remove(fo.configuration)
            self.list_content.remove(widget)
            self.functions.remove(fo)

    # noinspection PyUnusedLocal
    def on_up_clicked(self, widget):
        rowup = self.list_content.get_selected_row()
        if rowup is not None:
            index = rowup.get_index()
            if index > 0:
                newindex = index - 1
                widget = rowup.get_child()

                self.functions.remove(widget)
                self.functions.insert(newindex, widget)
                self.list_content.remove(rowup)
                rowup.remove(widget)
                self.list_content.insert(widget, newindex)
                self.list_content.select_row(self.list_content.get_row_at_index(newindex))

    # noinspection PyUnusedLocal
    def on_down_clicked(self, widget):
        rowdown = self.list_content.get_selected_row()
        if rowdown is not None:
            index = rowdown.get_index()
            if index < len(self.list_content) - 1:
                newindex = index + 1
                widget = rowdown.get_child()

                self.functions.remove(widget)
                self.functions.insert(newindex, widget)
                self.list_content.remove(rowdown)
                rowdown.remove(widget)
                self.list_content.insert(widget, newindex)
                self.list_content.select_row(self.list_content.get_row_at_index(newindex))

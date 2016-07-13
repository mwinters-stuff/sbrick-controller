import gi
from SBrickSequencePlayer import SBrickSequencePlayer

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk, GLib, Gio, GObject


class SequenceStepBox(Gtk.Box):
    def __init__(self, step_configuration, functions):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.set_homogeneous(False)
        self.step_configuration = step_configuration
        self.functions = functions
        self.sbrick = None

        self.show_all()

        self.function_group_model = Gtk.ListStore(str, str)
        self.function_model = Gtk.ListStore(str, str)

        # function group
        self.pack_start(Gtk.Label("Function Group:"), False, True, 0)
        self.combo_function_group = Gtk.ComboBoxText()
        self.combo_function_group.set_id_column(0)
        self.combo_function_group.set_model(self.function_group_model)
        renderer_text = Gtk.CellRendererText()
        self.combo_function_group.clear()
        self.combo_function_group.pack_start(renderer_text, True)
        self.combo_function_group.add_attribute(renderer_text, "text", 1)
        self.pack_start(self.combo_function_group, False, True, 0)
        self.combo_function_group.connect("changed", self.on_group_changed)

        # function group
        self.add(Gtk.Label("Function:"))
        self.combo_function = Gtk.ComboBoxText()
        self.combo_function.set_id_column(0)
        self.combo_function.set_model(self.function_model)
        renderer_text = Gtk.CellRendererText()
        self.combo_function.clear()
        self.combo_function.pack_start(renderer_text, True)
        self.combo_function.add_attribute(renderer_text, "text", 1)
        self.pack_start(self.combo_function, False, True, 0)

        self.pack_start(Gtk.Label("MS Delay After:"), False, True, 0)
        self.timeAdjustment = Gtk.Adjustment(1000, -1, 120000, 10, 100, 0.0)
        self.spinDelayAfter = Gtk.SpinButton.new(self.timeAdjustment, 10, 0)
        self.pack_start(self.spinDelayAfter, False, True, 0)

        self.update_group_model()

        if "function_group" in self.step_configuration:
            self.combo_function_group.set_active_id(self.step_configuration["function_group"])
            self.update_function_model(self.combo_function_group.get_active_id())

        if "function" in self.step_configuration:
            self.combo_function.set_active_id(self.step_configuration["function"])

        if "delay_time" in self.step_configuration:
            self.timeAdjustment.set_value(int(step_configuration["delay_time"]))

    def set_sbrick(self, sbrick):
        self.sbrick = sbrick

    def write_configuration(self):
        self.step_configuration["function_group"] = self.combo_function_group.get_active_id()
        self.step_configuration["function"] = self.combo_function.get_active_id()
        self.step_configuration["delay_time"] = self.timeAdjustment.get_value()

    def update_group_model(self):
        active_group = self.combo_function_group.get_active_id()
        self.function_group_model.clear()

        for group in self.functions:
            label = group["group"]
            self.function_group_model.append([label, label])
        if active_group is None:
            iterf = self.function_group_model.get_iter_first()
            if iterf:
                active_group = self.function_group_model.get_value(iterf, 0)
        self.combo_function_group.set_active_id(active_group)
        self.update_function_model(active_group)

    def update_function_model(self, group):
        active_function = self.combo_function.get_active_id()
        self.function_model.clear()
        for fgroup in self.functions:
            if fgroup["group"] == group:
                for func in fgroup["functions"]:
                    label = func["label"]
                    self.function_model.append([label, label])
        if active_function is None:
            iterf = self.function_model.get_iter_first()
            if iterf:
                active_function = self.function_model.get_value(iterf, 0)
        self.combo_function.set_active_id(active_function)

    # noinspection PyUnusedLocal
    def on_group_changed(self, widget):
        group = self.combo_function_group.get_active_id()
        self.update_function_model(group)


class SBrickSequenceBox(Gtk.Box):
    def __init__(self, configuration):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.set_homogeneous(False)
        self.sequence_player = None

        self.tool_bar = Gtk.Toolbar()
        self.pack_start(self.tool_bar, False, True, 0)

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

        self.tool_bar.insert(Gtk.SeparatorToolItem.new(), -1)

        self.tool_play = Gtk.ToolButton.new(Gtk.Image.new_from_stock(Gtk.STOCK_MEDIA_PLAY, Gtk.IconSize.BUTTON), "Run")
        self.tool_play.connect("clicked", self.on_run_clicked)
        self.tool_bar.insert(self.tool_play, -1)
        self.enable_tools(True, False)

        self.content = Gtk.ListBox()

        self.scrollTree = Gtk.ScrolledWindow()
        self.scrollTree.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrollTree.add_with_viewport(self.content)
        self.scrollTree.set_min_content_height(100)
        self.pack_start(self.scrollTree, True, True, 0)

        self.sbrickConfiguration = configuration
        self.sbrick = None
        self.sequenceSteps = []

        if "sequence" in self.sbrickConfiguration:
            for step in self.sbrickConfiguration["sequence"]:
                stepbox = SequenceStepBox(step, self.sbrickConfiguration["functions"])
                self.content.add(stepbox)
                self.sequenceSteps.append(stepbox)
        else:
            self.sbrickConfiguration["sequence"] = []

    def write_configuration(self):
        for step in self.sequenceSteps:
            step.write_configuration()

    # noinspection PyUnusedLocal
    def on_add_clicked(self, widget):
        step = dict()
        self.sbrickConfiguration["sequence"].append(step)
        stepbox = SequenceStepBox(step, self.sbrickConfiguration["functions"])
        self.content.add(stepbox)
        self.sequenceSteps.append(stepbox)
        self.show_all()

    # noinspection PyUnusedLocal
    def on_delete_clicked(self, widget):
        row = self.content.get_selected_row()
        if row is not None:
            ch = row.get_child()
            self.sbrickConfiguration["sequence"].remove(ch.step_configuration)
            self.content.remove(row)
            self.sequenceSteps.remove(ch)

    # noinspection PyUnusedLocal
    def on_up_clicked(self, widget):
        rowup = self.content.get_selected_row()
        if rowup is not None:
            index = rowup.get_index()
            if index > 0:
                newindex = index - 1
                widget = rowup.get_child()

                seqconfig = self.sbrickConfiguration["sequence"][index]
                self.sbrickConfiguration["sequence"].remove(seqconfig)
                self.sbrickConfiguration["sequence"].insert(newindex, seqconfig)

                self.sequenceSteps.remove(widget)
                self.sequenceSteps.insert(newindex, widget)
                self.content.remove(rowup)
                rowup.remove(widget)
                self.content.insert(widget, newindex)
                self.content.select_row(self.content.get_row_at_index(newindex))

    # noinspection PyUnusedLocal
    def on_down_clicked(self, widget):
        rowdown = self.content.get_selected_row()
        if rowdown is not None:
            index = rowdown.get_index()
            if index < len(self.sequenceSteps) - 1:
                newindex = index + 1
                widget = rowdown.get_child()

                seqconfig = self.sbrickConfiguration["sequence"][index]
                self.sbrickConfiguration["sequence"].remove(seqconfig)
                self.sbrickConfiguration["sequence"].insert(newindex, seqconfig)

                self.sequenceSteps.remove(widget)
                self.sequenceSteps.insert(newindex, widget)
                self.content.remove(rowdown)
                rowdown.remove(widget)
                self.content.insert(widget, newindex)
                self.content.select_row(self.content.get_row_at_index(newindex))

    def set_sbrick(self, sbrick):
        self.sbrick = sbrick
        self.enable_tools(True, sbrick is not None)
        for step in self.sequenceSteps:
            step.set_sbrick(sbrick)

    # noinspection PyUnusedLocal
    def on_run_clicked(self, widget):
        self.enable_tools(False, False)
        self.content.set_sensitive(False)
        self.write_configuration()
        self.sequence_player = SBrickSequencePlayer(self.sbrickConfiguration, self.sbrick)
        self.sequence_player.connect('sequence_finished', self.on_sequence_finished)
        self.sequence_player.start()

    # noinspection PyUnusedLocal
    def on_sequence_finished(self, sequence_player):
        print("sequece finished")
        if self.sequence_player == sequence_player:
            self.enable_tools(True, True)
            self.content.set_sensitive(True)
            # self.sequence_player.disconnect('sequence_finished')
            self.sequence_player = None

    def enable_tools(self, main, play):
        self.tool_add.set_sensitive(main)
        self.tool_delete.set_sensitive(main)
        self.tool_up.set_sensitive(main)
        self.tool_down.set_sensitive(main)
        self.tool_play.set_sensitive(play)

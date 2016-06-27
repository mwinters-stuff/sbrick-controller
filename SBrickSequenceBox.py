import gi

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
        if active_group == None:
            iter = self.function_group_model.get_iter_first()
            if iter:
                active_group = self.function_group_model.get_value(iter, 0)
                print(active_group)
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
        if active_function == None:
            iter = self.function_model.get_iter_first()
            if iter:
                active_function = self.function_model.get_value(iter, 0)
        self.combo_function.set_active_id(active_function)

    def on_group_changed(self, widget):
        group = self.combo_function_group.get_active_id()
        self.update_function_model(group)


class SBrickSequenceBox(Gtk.Box):
    def __init__(self, configuration):
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

        self.tool_bar.insert(Gtk.SeparatorToolItem.new(), -1)

        tool = Gtk.ToolButton.new(Gtk.Image.new_from_stock(Gtk.STOCK_MEDIA_PLAY, Gtk.IconSize.BUTTON), "Run")
        tool.connect("clicked", self.on_run_clicked)
        self.tool_bar.insert(tool, -1)

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

    def on_add_clicked(self, widget):
        step = dict()
        self.sbrickConfiguration["sequence"].append(step)
        stepbox = SequenceStepBox(step, self.sbrickConfiguration["functions"])
        self.content.add(stepbox)
        self.sequenceSteps.append(stepbox)
        self.show_all()

    def on_delete_clicked(self, widget):
        row = self.content.get_selected_row()
        ch = row.get_child()
        self.sbrickConfiguration["sequence"].remove(ch.step_configuration)
        self.content.remove(row)

    def set_sbrick(self, sbrick):
        self.sbrick = sbrick
        for step in self.sequenceSteps:
            step.set_sbrick(sbrick)

    def on_run_clicked(self, widget):
        pass

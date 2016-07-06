import gi

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences
from gi.repository import Gtk


class SBrickConfigureDialog(Gtk.Dialog):
    def __init__(self, parent, sbrick_configuration):
        Gtk.Dialog.__init__(self, "Configure SBrick", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.sbrickConfiguration = sbrick_configuration
        self.set_default_size(150, 100)

        self.channelTypeStore = Gtk.ListStore(str, str)
        self.channelTypeStore.append(["motor", "Motor"])
        self.channelTypeStore.append(["servo", "Servo"])
        self.content = self.get_content_area()

        hbox = Gtk.FlowBox()
        hbox.set_max_children_per_line(2)
        hbox.set_min_children_per_line(2)
        hbox.set_selection_mode(Gtk.SelectionMode.NONE)

        hbox.add(Gtk.Label("Name:"))
        self.edit_brick_name = Gtk.Entry()
        self.edit_brick_name.set_max_length(20)
        hbox.add(self.edit_brick_name)

        hbox.add(Gtk.Label("Address:"))
        self.edit_brick_address = Gtk.Entry()
        self.edit_brick_address.set_max_length(17)
        hbox.add(self.edit_brick_address)

        self.content.pack_start(hbox, False, True, 0)

        self.channel1_id_edit, self.channel1_name_edit, self.channel1_combo_type = self.create_channel_box(1)
        self.channel2_id_edit, self.channel2_name_edit, self.channel2_combo_type = self.create_channel_box(2)
        self.channel3_id_edit, self.channel3_name_edit, self.channel3_combo_type = self.create_channel_box(3)
        self.channel4_id_edit, self.channel4_name_edit, self.channel4_combo_type = self.create_channel_box(4)

        if "name" in self.sbrickConfiguration:
            self.edit_brick_name.set_text(self.sbrickConfiguration["name"])
        if "addr" in self.sbrickConfiguration:
            self.edit_brick_address.set_text(self.sbrickConfiguration["addr"])

        self.set_from_config(0, self.channel1_id_edit, self.channel1_name_edit, self.channel1_combo_type)
        self.set_from_config(1, self.channel2_id_edit, self.channel2_name_edit, self.channel2_combo_type)
        self.set_from_config(2, self.channel3_id_edit, self.channel3_name_edit, self.channel3_combo_type)
        self.set_from_config(3, self.channel4_id_edit, self.channel4_name_edit, self.channel4_combo_type)

        self.show_all()
        self.connect('response', self.on_response)

    # noinspection PyUnusedLocal
    def on_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            self.sbrickConfiguration["name"] = self.edit_brick_name.get_text()
            self.sbrickConfiguration["addr"] = self.edit_brick_address.get_text()
            self.sbrickConfiguration["channelConfiguration"] = []
            self.set_to_config(0, self.channel1_id_edit, self.channel1_name_edit, self.channel1_combo_type)
            self.set_to_config(1, self.channel2_id_edit, self.channel2_name_edit, self.channel2_combo_type)
            self.set_to_config(2, self.channel3_id_edit, self.channel3_name_edit, self.channel3_combo_type)
            self.set_to_config(3, self.channel4_id_edit, self.channel4_name_edit, self.channel4_combo_type)

    def create_channel_box(self, channel_number):
        hbox = Gtk.FlowBox()
        hbox.set_max_children_per_line(8)
        hbox.set_min_children_per_line(8)
        hbox.set_selection_mode(Gtk.SelectionMode.NONE)

        hbox.add(Gtk.Label("Channel: %d" % channel_number))

        hbox.add(Gtk.Label("ID:"))
        id_edit = Gtk.Entry()
        id_edit.set_max_length(5)
        hbox.add(id_edit)

        hbox.add(Gtk.Label("Name:"))
        name_edit = Gtk.Entry()
        name_edit.set_max_length(20)
        hbox.add(name_edit)
        hbox.add(Gtk.Label("Type:"))
        combo_type = Gtk.ComboBoxText()
        combo_type.set_id_column(0)
        combo_type.set_model(self.channelTypeStore)
        renderer_text = Gtk.CellRendererText()
        combo_type.clear()
        combo_type.pack_start(renderer_text, True)
        combo_type.add_attribute(renderer_text, "text", 1)
        hbox.add(combo_type)

        self.content.pack_start(hbox, False, True, 0)
        return id_edit, name_edit, combo_type

    def set_from_config(self, channel_index, id_edit, name_edit, combo_type):
        if "channelConfiguration" in self.sbrickConfiguration:
            channel = self.sbrickConfiguration["channelConfiguration"][channel_index]
            id_edit.set_text(channel["id"])
            name_edit.set_text(channel["name"])
            combo_type.set_active_id(channel["type"])

    def set_to_config(self, channel_index, id_edit, name_edit, combo_type):
        channel = dict()
        self.sbrickConfiguration["channelConfiguration"].append(channel)
        channel["id"] = id_edit.get_text()
        channel["name"] = name_edit.get_text()
        channel["type"] = combo_type.get_active_id()

import gi

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk


class SBrickServoChannelBox(Gtk.Frame):
    def __init__(self, channel, sbrick_channel):
        Gtk.Frame.__init__(self)
        self.sbrickChannel = sbrick_channel
        self.channel = channel
        self.sbrick = None
        self.set_label("Channel: %d - %s" % ((channel + 1), self.sbrickChannel["name"]))

        self.vbox = Gtk.FlowBox()#self, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.vbox.set_max_children_per_line(5)
        self.vbox.set_min_children_per_line(5)
        self.vbox.set_selection_mode(Gtk.SelectionMode.NONE)

        self.add(self.vbox)

        # self.vbox.pack_start(Gtk.Label("Angle: "), False, False, 0)
        self.vbox.add(Gtk.Label("Angle: "))

        self.positionButtons = []
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

        # self.vbox.pack_start(self.comboPosition, False, False, 0)
        self.vbox.add(self.comboPosition)
        self.comboPosition.connect("changed", self.on_comboposition_changed)
        self.comboPosition.set_active_id("0")

        # self.vbox.pack_start(Gtk.Label(""), False, True, 0)

        self.checkTime = Gtk.CheckButton("Time MS:")
        # self.vbox.pack_start(self.checkTime, False, False, 0)
        self.vbox.add(self.checkTime)
        self.checkTime.connect("toggled", self.on_time_toggled)

        self.timeAdjustment = Gtk.Adjustment(1000, -1, 10000, 10, 100, 0.0)
        self.spinTime = Gtk.SpinButton.new(self.timeAdjustment, 10, 0)
        # self.vbox.pack_start(self.spinTime, False, False, 0)
        self.vbox.add(self.spinTime)
        self.spinTime.set_sensitive(False)

        self.buttonGo = Gtk.Button("Move")
        self.buttonGo.connect("clicked", self.on_switch_go_clicked)
        self.vbox.add(self.buttonGo)
        # self.vbox.pack_start(self.buttonGo, False, False, 0)

        self.set_sensitive(False)
        self.pwm = 0
        self.on = False

    def on_switch_go_clicked(self, switch):
        if self.sbrick is not None:
            self.on = True
            timems = -1
            if self.checkTime.get_active():
                timems = self.spinTime.get_value_as_int()

            if self.pwm == 0:
                self.sbrick.stop(self.channel)
            else:
                self.sbrick.drive(self.channel, self.pwm, 0, timems)

    def on_comboposition_changed(self, combo):
        self.pwm = int(combo.get_active_id())
        if self.sbrick and self.on:
            self.sbrick.change_pwm(self.channel, self.pwm, True)

    def set_sbrick(self, sbrick):
        self.sbrick = sbrick
        self.set_sensitive(sbrick is not None)

    def stopped(self):
        self.on = False

    def on_time_toggled(self, checkbox):
        self.spinTime.set_sensitive(checkbox.get_active())

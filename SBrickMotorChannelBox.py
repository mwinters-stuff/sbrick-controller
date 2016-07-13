import gi

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk


class SBrickMotorChannelBox(Gtk.Frame):
    def __init__(self, channel, sbrick_channel):
        Gtk.Frame.__init__(self)

        self.sbrickChannel = sbrick_channel
        self.channel = channel
        self.sbrick = None
        self.set_label("Channel: %d - %s" % ((channel + 1), self.sbrickChannel["name"]))

        self.vbox = Gtk.FlowBox()  # , orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.vbox.set_border_width(2)
        self.vbox.set_max_children_per_line(7)
        self.vbox.set_min_children_per_line(7)
        self.vbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.add(self.vbox)

        # self.vbox.pack_start(Gtk.Label("PWM: "), True, False, 0)
        self.vbox.add(Gtk.Label("PWM: "))
        self.pwmAdjustment = Gtk.Adjustment(255, 0, 255, 5, 10, 0.0)
        self.spinPWM = Gtk.SpinButton.new(self.pwmAdjustment, 5, 0)
        # self.vbox.pack_start(self.spinPWM, True, False, 0)
        self.vbox.add(self.spinPWM)
        self.pwmAdjustment.connect("value-changed", self.on_pwm_changed)

        self.checkReverse = Gtk.CheckButton("Reverse")
        self.checkReverse.connect("toggled", self.on_reverse_changed)
        self.vbox.add(self.checkReverse)
        # self.vbox.pack_start(self.checkReverse, True, False, 0)

        self.checkTime = Gtk.CheckButton("Time MS:")
        # self.vbox.pack_start(self.checkTime, True, False, 0)
        self.vbox.add(self.checkTime)
        self.checkTime.connect("toggled", self.on_time_toggled)

        self.timeAdjustment = Gtk.Adjustment(1000, -1, 30000, 100, 1000, 0.0)
        self.spinTime = Gtk.SpinButton.new(self.timeAdjustment, 10, 0)
        # self.vbox.pack_start(self.spinTime, True, False, 0)
        self.vbox.add(self.spinTime)
        self.spinTime.set_sensitive(False)

        self.checkBrake = Gtk.CheckButton("Break Stop")
        # self.vbox.pack_start(self.checkBrake, True, False, 0)
        self.vbox.add(self.checkBrake)

        self.buttonGo = Gtk.Button("Start")
        self.buttonGo.connect("clicked", self.on_switch_go_clicked)
        # self.vbox.pack_start(self.buttonGo, True, False, 0)
        self.vbox.add(self.buttonGo)

        self.set_sensitive(False)
        self.on = False
        self.pwm = 0
        self.reverse = False

    # noinspection PyUnusedLocal
    def on_switch_go_clicked(self, switch):
        self.on = not self.on
        if self.sbrick is not None:
            pwm = self.spinPWM.get_value_as_int()
            timems = -1
            if self.checkTime.get_active():
                timems = self.spinTime.get_value_as_int()
            reverse = self.checkReverse.get_active()
            brakestop = self.checkBrake.get_active()

            if self.on:
                self.buttonGo.set_label("Stop")
                self.sbrick.drive(self.channel, pwm, reverse, timems, brakestop)
            else:
                self.sbrick.stop(self.channel, brakestop)
                self.buttonGo.set_label("Start")

    def set_sbrick(self, sbrick):
        self.sbrick = sbrick
        self.set_sensitive(sbrick is not None)

    def on_pwm_changed(self, adjustment):
        self.pwm = int(adjustment.get_value())
        if self.sbrick is not None and self.on:
            self.sbrick.change_pwm(self.channel, self.pwm)

    def on_reverse_changed(self, checkbox):
        self.reverse = checkbox.get_active()
        if self.sbrick is not None and self.on:
            self.sbrick.change_reverse(self.channel, self.reverse)

    def on_time_toggled(self, checkbox):
        self.spinTime.set_sensitive(checkbox.get_active())

    def stopped(self):
        self.buttonGo.set_label("Start")
        self.on = False

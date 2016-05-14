import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib


class SBrickMotorChannelBox(Gtk.Frame):
    def __init__(self, channel):
        Gtk.Frame.__init__(self)
        self.channel = channel
        self.sbrick = None
        self.set_label("Channel: " + str(channel + 1))

        self.vbox = Gtk.Box(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(self.vbox)

        self.vbox.pack_start(Gtk.Label("PWM: "), False, False, 0)
        self.pwmAdjustment = Gtk.Adjustment(255, 0, 255, 5, 10, 0.0)
        self.spinPWM = Gtk.SpinButton.new(self.pwmAdjustment,5,0)
        self.vbox.pack_start(self.spinPWM, False, False, 0)
        self.pwmAdjustment.connect("value-changed",self.on_pwm_changed)

        self.checkReverse = Gtk.CheckButton("Reverse")
        self.checkReverse.connect("toggled", self.on_reverse_changed)
        self.vbox.pack_start(self.checkReverse, False, False, 0)

        self.checkTime = Gtk.CheckButton("Time MS:")
        self.vbox.pack_start(self.checkTime, False, False, 0)
        self.checkTime.connect("toggled",self.on_time_toggled)

        self.timeAdjustment = Gtk.Adjustment(1000, -1, 10000, 10, 100, 0.0)
        self.spinTime = Gtk.SpinButton.new(self.timeAdjustment, 10, 0)
        self.vbox.pack_start(self.spinTime, False, False, 0)
        self.spinTime.set_sensitive(False)

        self.checkBrake= Gtk.CheckButton("Break Stop")
        self.vbox.pack_start(self.checkBrake, False, False, 0)

        self.switchGo = Gtk.Switch()
        self.switchGo.connect("state-set",self.on_switchGo_state_set)
        self.vbox.pack_start(self.switchGo, False, False, 0)

        self.set_sensitive(False)
        self.on = False


    def on_switchGo_state_set(self, switch, state):
        if(self.sbrick):
            self.on = state
            pwm = self.spinPWM.get_value_as_int()
            timeMs = -1
            if self.checkTime.get_active():
                timeMs = self.spinTime.get_value_as_int()
            reverse = self.checkReverse.get_active()
            brakestop = self.checkBrake.get_active()

            if(state):
                self.sbrick.drive(self.channel, pwm,reverse, timeMs, brakestop)
            else:
                self.sbrick.stop(self.channel,brakestop)

    def set_sbrick(self, sbrick):
        self.sbrick = sbrick
        self.set_sensitive(sbrick != None)

    def on_pwm_changed(self, adjustment):
        self.pwm = int(adjustment.get_value())
        if (self.sbrick and self.on):
            self.sbrick.change_pwm(self.channel,self.pwm)

    def on_reverse_changed(self, checkbox):
        self.reverse = checkbox.get_active()
        if (self.sbrick and self.on):
            self.sbrick.change_reverse(self.channel,self.reverse)

    def on_time_toggled(self, checkbox):
        self.spinTime.set_sensitive(checkbox.get_active())

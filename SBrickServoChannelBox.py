import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib


class SBrickServoChannelBox(Gtk.Frame):
    def __init__(self, channel):
        Gtk.Frame.__init__(self)
        self.channel = channel
        self.sbrick = None
        self.set_label("Channel: " + str(channel + 1))

        self.vbox = Gtk.Box(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(self.vbox)

        self.vbox.pack_start(Gtk.Label("Angle: "), False, False, 0)

        self.positionButtons = []
        self.pwmStore = Gtk.ListStore(int, str)
        self.pwmStore.append([-255, "-90.0"])
        self.pwmStore.append([-223, "-77.1"])
        self.pwmStore.append([-190, "-64.3"])
        self.pwmStore.append([-161, "-51.4"])
        self.pwmStore.append([-126, "-38.6"])
        self.pwmStore.append([-97, "-25.7"])
        self.pwmStore.append([-67, "-12.9"])
        self.pwmStore.append([0, "0.00"])
        self.pwmStore.append([67, "12.9"])
        self.pwmStore.append([97, "25.7"])
        self.pwmStore.append([126, "38.6"])
        self.pwmStore.append([161, "51.4"])
        self.pwmStore.append([190, "64.3"])
        self.pwmStore.append([223, "77.1"])
        self.pwmStore.append([255, "90.0"])

        self.comboPosition = Gtk.ComboBoxText()
        self.comboPosition.set_id_column(0)
        self.comboPosition.set_model(self.pwmStore)
        renderer_text = Gtk.CellRendererText()
        self.comboPosition.clear()
        self.comboPosition.pack_start(renderer_text, True)
        self.comboPosition.add_attribute(renderer_text, "text", 1)

        self.vbox.pack_start(self.comboPosition, False, False, 0)
        self.comboPosition.connect("changed", self.on_comboposition_changed)
        self.comboPosition.set_active(7)

        self.vbox.pack_start(Gtk.Label(""), False, True, 0)

        self.vbox.pack_start(Gtk.Label("Time MS: "), False, False, 0)
        self.timeAdjustment = Gtk.Adjustment(1000, -1, 10000, 10, 100, 0.0)
        self.spinTime = Gtk.SpinButton.new(self.timeAdjustment, 10, 0)
        self.vbox.pack_start(self.spinTime, False, False, 0)

        self.switchGo = Gtk.Switch()
        self.switchGo.connect("state-set", self.on_switchGo_state_set)
        self.vbox.pack_start(self.switchGo, False, False, 0)

        self.set_sensitive(False)
        self.pwm = 0
        self.on = False

    def on_switchGo_state_set(self, switch, state):
        if (self.sbrick):
            self.on = state
            timeMs = self.spinTime.get_value_as_int()

            if (state):
                if(self.pwm < 0):
                    self.sbrick.drive(self.channel, -self.pwm, 1, timeMs)
                else:
                    self.sbrick.drive(self.channel, self.pwm, 0, timeMs)
            else:
                self.sbrick.stop(self.channel)

    def on_comboposition_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            self.pwm = model[tree_iter][0]
            if (self.sbrick and self.on):
                self.sbrick.change_pwm(self.channel, self.pwm, True)


    def set_sbrick(self, sbrick):
        self.sbrick = sbrick
        self.set_sensitive(sbrick != None)

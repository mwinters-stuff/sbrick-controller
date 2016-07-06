import threading

from IdleObject import IdleObject
import gi

gi.require_version('Gtk', '3.0')

# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import GObject


class SBrickSequencePlayer(threading.Thread, IdleObject):
    def __init__(self, sbrick_configuration, sbrick_communications):
        threading.Thread.__init__(self)
        IdleObject.__init__(self)

        self.sbrick_configuration = sbrick_configuration
        self.sbrick_communications = sbrick_communications

        self.next_event = threading.Event()
        self.next_event.clear()

        self.sbrick_communications.connect('sbrick_connected', self.on_sbrick_connected)
        self.sbrick_communications.connect('sbrick_disconnected_error', self.on_sbrick_disconnected_error)
        self.sbrick_communications.connect('sbrick_disconnected_ok', self.on_sbrick_disconnected_ok)
        self.sbrick_communications.connect('sbrick_channel_stop', self.on_sbrick_channel_stop)
        self.sbrick_communications.connect('sbrick_drive_sent', self.on_sbrick_drive_sent)

    def __del__(self):
        print("sequence player destroyed")
        # self.sbrick_communications.disconnect('sbrick_connected')
        # self.sbrick_communications.disconnect('sbrick_disconnected_error')
        # self.sbrick_communications.disconnect('sbrick_disconnected_ok')
        # self.sbrick_communications.disconnect('sbrick_channel_stop')
        # self.sbrick_communications.disconnect('sbrick_drive_sent')

    def on_sbrick_connected(self, sbrick):
        pass

    def on_sbrick_disconnected_ok(self, sbrick):
        pass

    def on_sbrick_disconnected_error(self, sbrick, message):
        pass

    # noinspection PyUnusedLocal,PyUnusedLocal
    def on_sbrick_channel_stop(self, sbrick, channel):
        print("step channel stop")
        self.next_event.set()

    # noinspection PyUnusedLocal
    def on_sbrick_drive_sent(self, sbrick, channel, time):
        print("drive sent ", channel, time)
        if time <= 0:
            self.next_event.set()

    def run(self):
        for self.step in self.sbrick_configuration["sequence"]:
            function_group_c = self.step["function_group"]
            function_c = self.step["function"]
            delay_time = self.step["delay_time"]
            print("Sequence Step %s %s %d" % (function_group_c, function_c, delay_time))

            function_group = self.get_function_group(self.sbrick_configuration, function_group_c)
            if function_group is None:
                return
            function = self.get_function_in_group(function_group, function_c)
            if function is None:
                return
            channelname = function["channel"]
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
                self.sbrick_communications.drive(channelname, pwm, reverse, time, off == "brake")
            else:
                # stop
                self.sbrick_communications.stop(channelname, off == "brake")

            self.next_event.wait()
            self.next_event.clear()
            print("delay ", delay_time)
            self.next_event.wait(delay_time / 1000.0)
            self.next_event.clear()
        self.emit('sequence_finished')

    @staticmethod
    def get_function_group(sbrick_configuration, group):
        for gp in sbrick_configuration["functions"]:
            if group == gp["group"]:
                return gp
        return None

    @staticmethod
    def get_function_in_group(group, function):
        for f in group["functions"]:
            if function == f["label"]:
                return f
        return None


GObject.type_register(SBrickSequencePlayer)
GObject.signal_new("sequence_finished", SBrickSequencePlayer, GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE, ())

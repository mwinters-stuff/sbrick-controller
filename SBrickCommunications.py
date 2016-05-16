import threading
import gi
from monotonicTime import monotonic_time
import struct
from bluepy.btle import Peripheral, BTLEException

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import GObject

GObject.threads_init()


class _IdleObject(GObject.GObject):
    """
    Override GObject.GObject to always emit signals in the main thread
    by emmitting on an idle handler
    """

    def __init__(self):
        GObject.GObject.__init__(self)

    def emit(self, *args):
        GObject.idle_add(GObject.GObject.emit, self, *args)


class SBrickChannelDrive:
    def __init__(self, channel, event_send):
        self.channel = channel
        self.eventSend = event_send
        self.pwm = 0
        self.reverse = 0
        self.timems = 0
        self.timesec = 0
        self.braked = False
        self.brake_after_time = True
        self.timestarted = 0.0
        self.stopped = True
        self.in_brake_time = False
        self.brake_time_sec = 0.0

    def drive(self, pwm, reverse, time, brake_after_time=False):
        self.pwm = int(pwm)
        if reverse:
            self.reverse = 1
        else:
            self.reverse = 0
        self.braked = False
        self.brake_after_time = brake_after_time
        self.timems = time
        self.timesec = 0
        if self.timems > 0:
            self.timesec = time / 1000.0
            self.timestarted = monotonic_time()

    def stop(self, braked=False):
        self.pwm = 0
        self.braked = braked
        print 'stop', self.channel, self.braked

    def get_command_drive(self, cmdin):
        if not self.in_brake_time:
            if not self.braked and (not self.stopped or self.pwm > 0):
                self.stopped = self.pwm == 0
                print "drive ",self.channel, self.stopped, self.pwm
                return cmdin + chr(self.channel) + chr(self.reverse) + chr(self.pwm)
        return cmdin

    def get_command_brake(self, cmdin):
        if self.braked and not self.stopped:
            self.pwm = 0
            self.brake_time_sec = 1.0
            self.brake_after_time = False
            if not self.in_brake_time:
                self.in_brake_time = True
                self.timestarted = monotonic_time()
            print "get_command_brake ", self.channel
            return cmdin + chr(self.channel)
        return cmdin

    def get_channel(self):
        return self.channel

    def set_pwm(self, pwm, change_reverse=False):
        if pwm < 0:
            if change_reverse:
                self.reverse = 1
            self.pwm = -pwm
        else:
            if change_reverse:
                self.reverse = 0
            self.pwm = pwm

    def set_reverse(self, reverse):
        if reverse:
            self.reverse = 1
        else:
            self.reverse = 0

    def decrement_run_timer(self):
        if self.timems > 0:
            m = monotonic_time()
            if m - self.timestarted >= self.timesec:
                self.stop(self.brake_after_time)
                print "time ", m - self.timestarted, self.timesec
                self.timems = 0
                self.timesec = 0
                self.stopped = False
                return True
        return False


    def decrement_brake_timer(self):
        if self.brake_time_sec > 0:
            m = monotonic_time()
            td = m - self.timestarted
            # print 'decrement_brake_timer', self.channel, self.brake_time_sec, td

            if td >= self.brake_time_sec:
                self.stop(False)
                print "brake time ", td, self.timesec
                self.timems = 0
                self.timesec = 0
                self.brake_time_sec = 0.0
                self.in_brake_time = False
                return True
        return False


class SBrickCommunications(threading.Thread, _IdleObject):
    def __init__(self, sbrick_addr):
        threading.Thread.__init__(self)
        _IdleObject.__init__(self)

        self.lock = threading.RLock()
        self.drivingLock = threading.RLock()
        self.eventSend = threading.Event()

        self.sBrickAddr = sbrick_addr

        self.brickChannels = [
            SBrickChannelDrive(0, self.eventSend),
            SBrickChannelDrive(1, self.eventSend),
            SBrickChannelDrive(2, self.eventSend),
            SBrickChannelDrive(3, self.eventSend),
        ]
        self.SBrickPeripheral = None
        self.stopFlag = False
        self.characteristicRemote = None

    def terminate(self):
        self.stopFlag = True

    def is_driving(self):
        locked = self.drivingLock.acquire(False)
        if locked:
            self.drivingLock.release()
        return not locked

    def run(self):
        try:
            self.SBrickPeripheral = Peripheral(self.sBrickAddr)
            service = self.SBrickPeripheral.getServiceByUUID('4dc591b0-857c-41de-b5f1-15abda665b0c')
            characteristics = service.getCharacteristics()
            for characteristic in characteristics:
                if characteristic.uuid == '02b8cbcc-0e25-4bda-8790-a15f53e6010f':
                    self.characteristicRemote = characteristic

            if self.characteristicRemote is None:
                return

            self.emit('sbrick_connected')

            monotime = 0.0

            while not self.stopFlag:
                if monotonic_time() - monotime >= 0.1:
                    self.send_command()
                    monotime = monotonic_time()
                self.eventSend.wait(0.01)
                for channel in self.brickChannels:
                    if channel.decrement_run_timer():
                        monotime = 0.0
                        self.drivingLock.release()
                        print "stop run normal"
                        self.emit("sbrick_channel_stop", channel.channel)
                    if channel.decrement_brake_timer():
                        self.drivingLock.release()
                        print "stop brake timer"
                        monotime = 0.0
                        self.emit("sbrick_channel_stop", channel.channel)

            self.stop_all()
            self.send_command()
            self.SBrickPeripheral.disconnect()
            self.emit('sbrick_disconnected_ok')
        except BTLEException as ex:
            self.emit("sbrick_disconnected_error", ex.message)

    def drive(self, channel, pwm, reverse, time, brake_after_time=False):
        with self.lock:
            if channel < 4:
                self.brickChannels[channel].drive(pwm, reverse, time, brake_after_time)
            self.eventSend.set()

    def stop(self, channel, breaked=False):
        with self.lock:
            if channel < 4:
                self.brickChannels[channel].stop(breaked)
            self.eventSend.set()

    def stop_all(self):
        with self.lock:
            for channel in self.brickChannels:
                channel.stop()
            self.eventSend.set()

    def change_pwm(self, channel, pwm, change_reverse=False):
        with self.lock:
            if channel < 4:
                self.brickChannels[channel].set_pwm(pwm, change_reverse)
            self.eventSend.set()

    def change_reverse(self, channel, reverse):
        with self.lock:
            if channel < 4:
                self.brickChannels[channel].set_reverse(reverse)
            self.eventSend.set()

    def send_command(self):
        with self.lock:
            # try:
            drivecmd = chr(0x01)
            brakecmd = chr(0x00)
            for channel in self.brickChannels:
                drivecmd = channel.get_command_drive(drivecmd)
                brakecmd = channel.get_command_brake(brakecmd)
            if len(drivecmd) > 1:
                self.drivingLock.acquire()
                self.characteristicRemote.write(drivecmd, True)
                self.print_hex_string("drive sent", drivecmd)
            if len(brakecmd) > 1:
                self.characteristicRemote.write(brakecmd, True)
                self.print_hex_string("brake sent", brakecmd)
                # return True
                # except Exception as ex:
                #     self.emit("sbrick_disconnected_error",ex.message)
                #     return False

    def disconnect(self):
        with self.lock:
            self.stopFlag = True

    @staticmethod
    def print_hex_string(what, strin):
        out = what + " -> "
        for chrx in strin:
            out = "%s %0X" % (out, ord(chrx))
        print out

    def get_voltage(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x0f) + chr(0x00))
                value = self.characteristicRemote.read()
                valueint = struct.unpack("<H", value)[0]
                return (valueint * 0.83875) / 2047.0
            except BTLEException as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_temperature(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x0f) + chr(0x0e))
                value = self.characteristicRemote.read()
                valueint = struct.unpack("<H", value)[0]
                return valueint / 118.85795 - 160
            except BTLEException as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_thermal_limit(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x15))
                value = self.characteristicRemote.read()
                valueint = struct.unpack("<H", value)[0]
                return valueint / 118.85795 - 160
            except BTLEException as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_watchdog_timeout(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x0e))
                value = self.characteristicRemote.read()
                return struct.unpack("<B", value)[0] * 0.1
            except BTLEException as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_authentication_timeout(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x09))
                value = self.characteristicRemote.read()
                return struct.unpack("<B", value)[0] * 0.1
            except BTLEException as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_power_cycle_counter(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x28))
                value = self.characteristicRemote.read()
                return struct.unpack("<I", value)[0]
            except BTLEException as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_uptime(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x29))
                value = self.characteristicRemote.read()
                seconds = struct.unpack("<I", value)[0] * 0.1
                minutes = seconds // 60
                hours = minutes // 60
                return "%02d:%02d:%02d" % (hours, minutes % 60, seconds % 60)
            except BTLEException as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_hardware_version(self):
        try:
            return self.SBrickPeripheral.readCharacteristic(0x000c)
        except BTLEException as ex:
            self.emit("sbrick_disconnected_error", ex.message)

    def get_software_version(self):
        try:
            return self.SBrickPeripheral.readCharacteristic(0x000a)
        except BTLEException as ex:
            self.emit("sbrick_disconnected_error", ex.message)

    def get_brick_id(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x0a))
                value = self.characteristicRemote.read()
                return "%0X %0X %0X %0X %0X %0X" % (
                    ord(value[0]), ord(value[1]), ord(value[2]), ord(value[3]), ord(value[4]), ord(value[5]))
            except BTLEException as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_need_authentication(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x02))
                value = self.characteristicRemote.read()
                return struct.unpack("<B", value)[0] == 1
            except BTLEException as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_is_authenticated(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x03))
                value = self.characteristicRemote.read()
                return struct.unpack("<B", value)[0] == 1
            except BTLEException as ex:
                self.emit("sbrick_disconnected_error", ex.message)


GObject.type_register(SBrickCommunications)
GObject.signal_new("sbrick_connected", SBrickCommunications, GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE, ())
GObject.signal_new("sbrick_disconnected_error", SBrickCommunications, GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE,
                   [GObject.TYPE_STRING])
GObject.signal_new("sbrick_disconnected_ok", SBrickCommunications, GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE, ())
GObject.signal_new("sbrick_channel_stop", SBrickCommunications, GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE,
                   [GObject.TYPE_INT])

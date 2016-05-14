import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
import struct
from bluepy.btle import Scanner, DefaultDelegate, Peripheral
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
    def __init__(self, channel, eventSend):
        self.channel = channel
        self.eventSend= eventSend
        self.pwm = 0
        self.reverse = 0
        self.time = 1000
        self.braked = False
        self.brake_after_time = True

    def on_timer(self):
        self.stop(self.brake_after_time)
        self.eventSend.set()

    def drive(self,pwm, reverse,time, brake_after_time = False):
        self.pwm = int(pwm)
        if(reverse):
            self.reverse = 1
        else:
            self.reverse = 0
        self.time = time
        self.braked = False
        self.brake_after_time = brake_after_time
        if(self.time > 0):
            t = threading.Timer(self.time / 1000.0,self.on_timer)
            t.start()
#        print "drive %d %d %d %d " % (self.channel, self.pwm, self.reverse, self.time)

    def stop(self, breaked = False):
        print "stop %d" % (self.channel)
        self.pwm = 0
        self.braked = breaked


    def get_command_drive(self, cmdin):
        if(not self.braked):
            return cmdin + chr(self.channel) + chr(self.reverse) + chr(self.pwm)
        return cmdin

    def get_command_brake(self, cmdin):
        if(self.braked):
            return cmdin + chr(self.channel)
        return cmdin

    def get_channel(self):
        return self.channel

    def set_pwm(self, pwm, changeReverse = False):
        if(pwm < 0):
            if(changeReverse):
                self.reverse = 1
            self.pwm = -pwm
        else:
            if(changeReverse):
                self.reverse = 0
            self.pwm = pwm


    def set_reverse(self, reverse):
        if(reverse):
            self.reverse = 1
        else:
            self.reverse = 0



class SBrickCommunications (threading.Thread, _IdleObject):
    def __init__(self, sBrickAddr ):
        threading.Thread.__init__(self)
        _IdleObject.__init__(self)

        self.lock = threading.RLock()
        self.eventSend = threading.Event()

        self.sBrickAddr = sBrickAddr

        self.brickChannels = [
            SBrickChannelDrive(0, self.eventSend),
            SBrickChannelDrive(1, self.eventSend),
            SBrickChannelDrive(2, self.eventSend),
            SBrickChannelDrive(3, self.eventSend),
        ]
        self.SBrickPeripheral = None
        self.stopFlag = False
        self.characteristicRemote = None

        self.lastdrivecmd = ""

    def terminate(self):
        self.stopFlag = True

    def run(self):
        try:
            self.SBrickPeripheral = Peripheral(self.sBrickAddr)
            service = self.SBrickPeripheral.getServiceByUUID('4dc591b0-857c-41de-b5f1-15abda665b0c')
            characteristics = service.getCharacteristics()
            for characteristic in characteristics:
                if characteristic.uuid == '02b8cbcc-0e25-4bda-8790-a15f53e6010f':
                    self.characteristicRemote = characteristic

            if self.characteristicRemote == None:
                return

    #        print "characteristic uuid %s handle %X " % (self.characteristicRemote.uuid,self.characteristicRemote.getHandle())
    #        print self.characteristicRemote.propertiesToString()
            self.emit('sbrick_connected')

            while self.stopFlag == False:
                self.send_command()
                self.eventSend.wait(0.2)
            self.stop_all()
            self.send_command()
            self.SBrickPeripheral.disconnect()
            self.emit('sbrick_disconnected_ok')
        except Exception as ex:
            self.emit("sbrick_disconnected_error", ex.message)

    def drive(self,channel, pwm, reverse, time, brake_after_time = False):
        with self.lock:
            if(channel < 4):
                self.brickChannels[channel].drive(pwm,reverse,time, brake_after_time)
        self.eventSend.set()

    def stop(self,channel, breaked = False):
        with self.lock:
            if (channel < 4):
                self.brickChannels[channel].stop(breaked)
        self.eventSend.set()

    def stop_all(self):
        with self.lock:
            for channel in self.brickChannels:
                channel.stop()
        self.eventSend.set()

    def change_pwm(self, channel, pwm, changeReverse = False):
        with self.lock:
            if(channel < 4):
                self.brickChannels[channel].set_pwm(pwm,changeReverse)
        self.eventSend.set()

    def change_reverse(self, channel, reverse):
        with self.lock:
            if(channel < 4):
                self.brickChannels[channel].set_reverse(reverse)
        self.eventSend.set()

    def send_command(self):
        with self.lock:
            try:
                drivecmd = chr(0x01)
                brakecmd = chr(0x00)
                for channel in self.brickChannels:
                    drivecmd = channel.get_command_drive(drivecmd)
                    brakecmd = channel.get_command_brake(brakecmd)
                if(len(drivecmd) > 1):
                    self.characteristicRemote.write(drivecmd,True)
                if (len(brakecmd) > 1):
                    self.characteristicRemote.write(brakecmd,True)
            except Exception as ex:
                self.emit("sbrick_disconnected_error",ex.message)

    def disconnect(self):
        with self.lock:
            self.stopFlag = True


    def print_hex_string(self, what, strin):
        out = what + " -> "
        for chrx in strin:
            out = "%s %0X" % (out,ord(chrx))
        print out

    def get_voltage(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x0f) + chr(0x00))
                value = self.characteristicRemote.read()
                valueint = struct.unpack("<H",value)[0]
                return (valueint * 0.83875) / 2047.0
            except Exception as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_temperature(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x0f) + chr(0x0e))
                value = self.characteristicRemote.read()
                valueint = struct.unpack("<H", value)[0]
                return valueint / 118.85795 - 160
            except Exception as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_thermal_limit(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x15))
                value = self.characteristicRemote.read()
                valueint = struct.unpack("<H", value)[0]
                return valueint / 118.85795 - 160
            except Exception as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_watchdog_timeout(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x0e))
                value = self.characteristicRemote.read()
                return struct.unpack("<B", value)[0] * 0.1
            except Exception as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_power_cycle_counter(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x28))
                value = self.characteristicRemote.read()
                return struct.unpack("<I", value)[0]
            except Exception as ex:
                self.emit("sbrick_disconnected_error", ex.message)

    def get_uptime_counter(self):
        with self.lock:
            try:
                self.characteristicRemote.write(chr(0x29))
                value = self.characteristicRemote.read()
                seconds = struct.unpack("<I", value)[0] * 0.1
                minutes = seconds // 60
                hours = minutes // 60
                return "%02d:%02d:%02d" % (hours, minutes % 60, seconds % 60)
            except Exception as ex:
                self.emit("sbrick_disconnected_error", ex.message)

GObject.type_register(SBrickCommunications)
GObject.signal_new("sbrick_connected", SBrickCommunications, GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE, ())
GObject.signal_new("sbrick_disconnected_error", SBrickCommunications, GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE, [GObject.TYPE_STRING])
GObject.signal_new("sbrick_disconnected_ok", SBrickCommunications, GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE, ())

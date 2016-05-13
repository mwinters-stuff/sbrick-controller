import threading
import time
from bluepy.btle import Scanner, DefaultDelegate, Peripheral

class SBrickChannelDrive:
    def __init__(self, channel):
        self.channel = channel
        self.pwm = 0
        self.reverse = 1
        self.time = 1000
        self.braked = False

    def drive(self,pwm, reverse,time):
        self.pwm = int(pwm)
        if(reverse):
            self.reverse = 1
        else:
            self.reverse = 0
        self.time = time
        self.braked = False
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



class SBrickCommunications (threading.Thread):
    def __init__(self, sBrickAddr ):
        threading.Thread.__init__(self)
        self.lock = threading.RLock()
        self.eventSend = threading.Event()

        self.sBrickAddr = sBrickAddr

        self.brickChannels = [
            SBrickChannelDrive(0),
            SBrickChannelDrive(1),
            SBrickChannelDrive(2),
            SBrickChannelDrive(3),
        ]
        self.SBrickPeripheral = None
        self.stopFlag = False
        self.characteristicRemote = None

        self.lastdrivecmd = ""

    def terminate(self):
        self.stopFlag = True

    def run(self):
        self.SBrickPeripheral = Peripheral(self.sBrickAddr)
        service = self.SBrickPeripheral.getServiceByUUID('4dc591b0-857c-41de-b5f1-15abda665b0c')
        characteristics = service.getCharacteristics()
        for characteristic in characteristics:
            if characteristic.uuid == '02b8cbcc-0e25-4bda-8790-a15f53e6010f':
                self.characteristicRemote = characteristic

        if self.characteristicRemote == None:
            return

        print "characteristic uuid %s handle %X " % (self.characteristicRemote.uuid,self.characteristicRemote.getHandle())
        print self.characteristicRemote.propertiesToString()

        while self.stopFlag == False:
            self.send_command()
            self.eventSend.wait(0.2)
        self.stop_all()
        self.send_command()
        self.SBrickPeripheral.disconnect()

    def drive(self,channel, pwm, reverse, time):
        with self.lock:
            if(channel < 4):
                self.brickChannels[channel].drive(pwm,reverse,time)
        self.eventSend.set()

    def stop(self,channel):
        with self.lock:
            if (channel < 4):
                self.brickChannels[channel].stop()
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
            drivecmd = chr(0x01)
            brakecmd = chr(0x00)
            for channel in self.brickChannels:
                drivecmd = channel.get_command_drive(drivecmd)
                brakecmd = channel.get_command_brake(brakecmd)
            if(len(drivecmd) > 1):
                self.characteristicRemote.write(drivecmd,True)
            if (len(brakecmd) > 1):
                self.characteristicRemote.write(brakecmd,True)

    def disconnect(self):
        with self.lock:
            self.stopFlag = True


    def print_hex_string(self, what, strin):
        out = what + " -> "
        for chrx in strin:
            out = "%s %0X" % (out,ord(chrx))
        print out
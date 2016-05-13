#!/usr/bin/env python
import gi

from SBrickServoChannelBox import SBrickServoChannelBox

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
#from gi.repository import GLib

from SBrickMotorChannelBox import SBrickMotorChannelBox
from SBrickCommunications import SBrickCommunications
import simplejson as json
import traceback, sys

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self,title="SBrick Controller")
        self.SBRICK_FW_VS = 0.0
        self.set_default_size(800,480)
        self.connect("delete-event",self.onDeleteWindow)

        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.mainBox.set_margin_bottom(10)
        self.mainBox.set_margin_top(10)
        self.mainBox.set_margin_left(10)
        self.mainBox.set_margin_right(10)
        self.add(self.mainBox)

        self.sbrickBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.mainBox.pack_start(self.sbrickBox, False, True, 0)

        self.sbrickBox.pack_start(Gtk.Label("SBricks: "), False, True, 0)

        self.comboSBrick = Gtk.ComboBoxText()
        self.comboSBrick.set_entry_text_column(0)
        self.comboSBrick.connect("changed", self.on_comboboxSBricks_changed)

        self.sbrickBox.pack_start(self.comboSBrick, True, True, 0)
        self.config = None

        self.read_config()


        self.checkConnect = Gtk.CheckButton("Connect")
        self.checkConnect.set_sensitive(False)
        self.checkConnect.connect("toggled",self.on_checkbuttonConnect_toggled)
        self.sbrickBox.pack_start(self.checkConnect, False, True, 0)

        self.currentSBrickChannels = []
        # self.SBrickChannel1 = SBrickChannelBox(0)
        # self.mainBox.pack_start(self.SBrickChannel1,False,True,0)
        #
        # self.SBrickChannel2 = SBrickChannelBox(1)
        # self.mainBox.pack_start(self.SBrickChannel2,False,True,0)
        #
        # self.SBrickChannel3 = SBrickChannelBox(2)
        # self.mainBox.pack_start(self.SBrickChannel3,False,True,0)
        #
        # self.SBrickChannel4 = SBrickChannelBox(3)
        # self.mainBox.pack_start(self.SBrickChannel4,False,True,0)
        self.sbrickCommunications = None


    def onDeleteWindow(self, *args):
        if(self.sbrickCommunications):
            self.sbrickCommunications.disconnect()
        Gtk.main_quit(*args)

    def on_mainWindow_show(self, widget):
        print ("main window show")
        # self.devices = self.scanner.scan(10.0)

    def on_comboboxSBricks_changed(self, combo):
        text = combo.get_active_text()
        self.checkConnect.set_sensitive(text != None)

        for widget in self.currentSBrickChannels:
            self.mainBox.remove(widget)
        self.currentSBrickChannels = []

        if(text != None):
            try:
                sbrick = self.find_sbrick_config(text)
                for channelNumber in range(4):
                    channelBox = None
                    cc = sbrick["channelConfiguration"][channelNumber]
                    if cc == 'motor':
                        channelBox = SBrickMotorChannelBox(channelNumber)
                    elif cc == 'servo':
                        channelBox = SBrickServoChannelBox(channelNumber)
                    self.mainBox.pack_start(channelBox, False, True, 0)
                    self.currentSBrickChannels.append(channelBox)
                self.mainBox.show_all()
            except Exception:
                traceback.print_exc(file=sys.stdout)



    def find_sbrick_config(self, comboString):
        for sbrick in self.config:
          str = "%s (%s)" % (sbrick["name"], sbrick["addr"])
          if(str == comboString):
              return sbrick
        return None


    def on_checkbuttonConnect_toggled(self,checkbutton):
        print("check button clicked")

        # self.buttonScan.set_sensitive(not checkbutton.get_active())
        self.comboSBrick.set_sensitive(not checkbutton.get_active())
        if(checkbutton.get_active()):
            sbrick = self.find_sbrick_config(self.comboSBrick.get_active_text())
            self.sbrickCommunications = SBrickCommunications(sbrick["addr"])
            self.sbrickCommunications.start()
        else:
            self.sbrickCommunications.stop_all()
            self.sbrickCommunications.disconnect()
            self.sbrickCommunications = None
        for widget in self.currentSBrickChannels:
            widget.set_sbrick(self.sbrickCommunications)


    def read_config(self):
        fp = open("sbricks.json")
        try:
            self.config = json.load(fp)
        finally:
            self.close()
        for sbrick in self.config:
            self.comboSBrick.append_text("%s (%s)" % (sbrick["name"], sbrick["addr"]) )


window = MainWindow()
window.show_all()
Gtk.main()


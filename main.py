#!/usr/bin/env python3
import gi
import sys

import simplejson as json

from MainWindow import MainWindow

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk, GLib, Gio

class SBrickApplication(Gtk.Application):
    def __init__(self, *args, **kwargs):
        # super(*args, **kwargs)
        Gtk.Application.__init__(self,*args,
                       application_id="nz.winters.sbrickapp",
                        flags=Gio.ApplicationFlags.NON_UNIQUE,
                         **kwargs)
        self.window = None
        self.config = None
        self.configFile = "sbricks.json"

        self.add_main_option("config", ord("c"), GLib.OptionFlags.OPTIONAL_ARG,
                              GLib.OptionArg.STRING, "Config File", None)
        self.connect('handle-local-options',self.on_handle_local_options)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        action = Gio.SimpleAction.new("save_configuration", None)
        action.connect("activate", self.on_save_configuration)
        self.add_action(action)

        builder = Gtk.Builder.new_from_file("menu.xml",)
        self.set_app_menu(builder.get_object("app-menu"))

    def do_activate(self):
        self.read_config()
        if not self.window:
            self.window = MainWindow(application=self,title="SBrick Controller", config=self.config)
        self.window.present()

    def on_handle_local_options(self, application, options):
        if options.contains("config"):
            self.configFile = options.lookup_value("config").get_string()
        return -1

    def on_quit(self,action,param):
        self.quit()

    def read_config(self):
        fp = open(self.configFile)
        try:
            self.config = json.load(fp)
        finally:
            fp.close()

    def on_about(self, action, param):
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about_dialog.present()

    def on_save_configuration(self, saction, param):
        fp = open(self.configFile, mode="w+")
        try:
            json.dump(self.config, fp, indent=2)
        finally:
            fp.close()

if __name__ == "__main__":
    app = SBrickApplication()
    app.run(sys.argv)

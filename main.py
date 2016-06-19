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

        action = Gio.SimpleAction.new("open_configuration", None)
        action.connect("activate", self.on_open_configuration)
        self.add_action(action)

        action = Gio.SimpleAction.new("save_configuration", None)
        action.connect("activate", self.on_save_configuration)
        self.add_action(action)

        action = Gio.SimpleAction.new("save_as_configuration", None)
        action.connect("activate", self.on_save_as_configuration)
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
        about_dialog.run()
        about_dialog.destroy()

    def on_save_configuration(self, action, param):
        self.save_configuration(self.configFile)

    def save_configuration(self, filename):
        fp = open(filename, mode="w+")
        try:
            json.dump(self.config, fp, indent=2)
        finally:
            fp.close()

    def on_save_as_configuration(self, action, param):
        dialog = Gtk.FileChooserDialog("Save Configuration As...", self.window,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_filename(self.configFile)

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.configFile = dialog.get_filename()
            self.save_configuration(self.configFile)

        dialog.destroy()

    def on_open_configuration(self, action, param):
        dialog = Gtk.FileChooserDialog("Open Configuration...", self.window,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        dialog.set_filename(self.configFile)

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.configFile = dialog.get_filename()
            self.read_config()
            if self.window:
                self.window.close()
            self.window = MainWindow(application=self, title="SBrick Controller", config=self.config)
            self.window.present()

            # self.save_configuration(self.configFile)

        dialog.destroy()

    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("JSON files")
        filter_text.add_pattern("*.json")
        dialog.add_filter(filter_text)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

if __name__ == "__main__":
    app = SBrickApplication()
    app.run(sys.argv)

import gi

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences
from gi.repository import Gtk


class ChannelConfigureDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Configure SBrick Channels", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        self.input = Gtk.Entry()
        self.input.set_max_length(8)

        box = self.get_content_area()
        box.add(self.input)
        self.show_all()

    def get_password(self):
        return self.input.get_text()

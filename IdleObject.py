import gi

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

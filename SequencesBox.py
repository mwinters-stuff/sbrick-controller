import gi

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk, GObject
from SBrickSequencePlayer import SBrickSequencePlayer
from SBrickCommunications import SBrickCommunications


class SequencePlayerBox(Gtk.Box):
    def __init__(self, sbrick_configuration, sbrick_communications_store):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin=5)
        self.set_homogeneous(False)
        self.sbrick_configuration = sbrick_configuration
        self.sbrick_communications_store = sbrick_communications_store
        self.sbrick_communications_store.add_observer(self)

        label = Gtk.Label(sbrick_configuration["name"])
        label.set_width_chars(20)
        label.set_justify(Gtk.Justification.LEFT)
        self.pack_start(label, False, True, 0)

        self.handler_ids = []
        self.sequence_player_handler_id = None

        self.button_play = Gtk.Button.new()
        self.button_play.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_MEDIA_PLAY, Gtk.IconSize.BUTTON))
        self.button_play.connect("clicked", self.on_play_clicked)
        self.pack_start(self.button_play, False, True, 0)

        self.checkPause = Gtk.CheckButton("Pause in Play All")
        self.checkPause.connect("toggled", self.on_pause_changed)
        self.pack_start(self.checkPause, False, True, 0)
        self.sbrick_communications = None
        self.sequence_player = None

    def dict_changed(self, dict, key):
        if dict == self.sbrick_communications_store and key == self.sbrick_configuration["addr"]:
            if self.sbrick_configuration["addr"] in self.sbrick_communications_store:
                self.sbrick_communications = self.sbrick_communications_store[self.sbrick_configuration["addr"]]
                self.handler_ids.append(
                    self.sbrick_communications.connect('sbrick_connected', self.on_sbrick_connected))
                self.handler_ids.append(
                    self.sbrick_communications.connect('sbrick_disconnected_error', self.on_sbrick_disconnected_error))
                self.handler_ids.append(
                    self.sbrick_communications.connect('sbrick_disconnected_ok', self.on_sbrick_disconnected_ok))
            else:
                for id in self.handler_ids:
                    self.sbrick_communications.disconnect(id)
                self.sbrick_communications = None
                self.handler_ids.clear()

    def on_pause_changed(self, widget):
        pass

    def on_play_clicked(self, widget):
        self.play(False)

    def play(self, from_player):
        if from_player and self.checkPause.get_active():
            self.emit('sequence_finished')
            return

        if "sequence" not in self.sbrick_configuration or len(self.sbrick_configuration["sequence"]) == 0:
            self.emit('sequence_finished')
            return

        if not self.sbrick_communications:
            self.connect_to_sbrick()

        self.button_play.set_sensitive(False)
        self.sequence_player = SBrickSequencePlayer(self.sbrick_configuration, self.sbrick_communications)
        self.sequence_player_handler_id = self.sequence_player.connect('sequence_finished', self.on_sequence_finished)
        self.sequence_player.start()

    def on_sequence_finished(self, sequence_player):
        if self.sequence_player == sequence_player:
            self.sequence_player.cleanup()
            self.button_play.set_sensitive(True)
            self.sequence_player.disconnect(self.sequence_player_handler_id)
            self.sequence_player = None
            self.emit('sequence_finished')

    def connect_to_sbrick(self):
        self.sbrick_communications = SBrickCommunications(self.sbrick_configuration["addr"])
        self.sbrick_communications_store[self.sbrick_configuration["addr"]] = self.sbrick_communications
        for channelNumber in range(4):
            sb = self.sbrick_configuration["channelConfiguration"][channelNumber]
            self.sbrick_communications.set_channel_config_id(channelNumber, sb["id"])

        self.sbrick_communications.connect('sbrick_connected', self.on_sbrick_connected)
        self.sbrick_communications.connect('sbrick_disconnected_error', self.on_sbrick_disconnected_error)
        self.sbrick_communications.connect('sbrick_disconnected_ok', self.on_sbrick_disconnected_ok)
        self.sbrick_communications.connect('sbrick_channel_stop', self.on_sbrick_channel_stop)

        passwd = None
        if "ownerPassword" in self.sbrick_configuration:
            passwd = self.sbrick_configuration["ownerPassword"]

        self.sbrick_communications.connect_to_sbrick(passwd)

    def on_sbrick_connected(self, sbrick):
        self.button_play.set_sensitive(True)

    def on_sbrick_disconnected_error(self, sbrick_communications, message):
        self.checkPause.set_active(True)
        self.on_sequence_finished(self.sequence_player)
        self.button_play.set_sensitive(True)

    def on_sbrick_disconnected_ok(self, sbrick):
        self.button_play.set_sensitive(True)

    def on_sbrick_channel_stop(self, sbrick, channel):
        pass


class SequencesBox(Gtk.Box):
    def __init__(self, configuration, sbrick_communications_store):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=3, margin=0)
        self.set_homogeneous(False)
        self.configuration = configuration
        self.sbrick_communications_store = sbrick_communications_store

        self.tool_bar = Gtk.Toolbar()
        self.pack_start(self.tool_bar, False, True, 0)

        self.action_play_all = Gtk.ToolButton.new(Gtk.Image.new_from_stock(Gtk.STOCK_MEDIA_PLAY, Gtk.IconSize.BUTTON),
                                                  "Play All")
        self.action_play_all.connect("clicked", self.on_play_all_clicked)
        self.tool_bar.insert(self.action_play_all, -1)
        self.action_stop_all = Gtk.ToolButton.new(Gtk.Image.new_from_stock(Gtk.STOCK_MEDIA_STOP, Gtk.IconSize.BUTTON),
                                                  "Stop All")
        self.action_stop_all.connect("clicked", self.on_stop_all_clicked)
        self.tool_bar.insert(self.action_stop_all, -1)
        self.content = Gtk.ListBox()

        self.scrollTree = Gtk.ScrolledWindow()
        self.scrollTree.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrollTree.add_with_viewport(self.content)
        self.scrollTree.set_min_content_height(100)
        self.pack_start(self.scrollTree, True, True, 0)

        self.sequence_count = 0
        if self.configuration is not None:
            for sbrick in self.configuration:
                stepbox = SequencePlayerBox(sbrick, sbrick_communications_store)
                stepbox.connect("sequence_finished", self.on_sequence_finished)
                self.content.add(stepbox)
                self.sequence_count = self.sequence_count + 1
        self.playing = False
        self.playing_sequence = None
        self.playing_index = -1

    def on_sequence_finished(self, sequence_player_box):
        if self.playing:
            self.playing_index = self.playing_index + 1
            if self.playing_index >= self.sequence_count:
                self.playing_index = 0
            self.play_step()

    def on_play_all_clicked(self, widget):
        self.action_play_all.set_sensitive(False)
        self.action_stop_all.set_sensitive(True)
        self.playing = True
        self.playing_index = 0
        self.play_step()

    def play_step(self):
        self.playing_sequence = self.content.get_row_at_index(self.playing_index).get_child()
        self.content.select_row(self.content.get_row_at_index(self.playing_index))
        self.playing_sequence.play(True)

    def on_stop_all_clicked(self, widget):
        self.action_play_all.set_sensitive(True)
        self.action_stop_all.set_sensitive(False)
        self.playing = False

    def disconnect_sbrick(self):
        pass

    def write_configuration(self):
        pass


GObject.type_register(SequencePlayerBox)
GObject.signal_new("sequence_finished", SequencePlayerBox, GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE, ())

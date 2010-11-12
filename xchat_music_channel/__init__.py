import rb
import rhythmdb
import dbus
import gconf

from xchat_music_channel.conf import gconf_keys, ConfDialog

from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)


class XChatMusicChannelPlugin(rb.Plugin):
    def activate(self, shell):        
        gc = gconf.client_get_default()
        self.server = gc.get_string(gconf_keys['server'])
        self.channel = gc.get_string(gconf_keys['channel'])
        
        self.shell = shell
        self.player = shell.get_player()
        self.event_id = self.player.connect('playing-song-changed', self.song_changed)
        
        self.bus = dbus.SessionBus()
        self.signal = None
        self.xchat_object = None
        self.xchat_hook = None
        self.xchat_context = None
    
    def deactivate(self, shell):
        del self.xchat_context
        if self.xchat_hook:
            self.signal.remove()
            self.get_xchat().Unhook(self.xchat_hook)
        del self.xchat_hook
        self.player.disconnect(self.event_id)
        del self.event_id
        del self.player
        del self.shell
        del self.channel
        del self.server
        del self.signal
        del self.bus
    
    def get_xchat(self):
        xchat_object = self.bus.get_object('org.xchat.service', '/org/xchat/Remote')
        return dbus.Interface(xchat_object, 'org.xchat.plugin')
    
    def song_changed(self, player, entry):
        xchat = self.get_xchat()
        self.xchat_context = xchat.FindContext(self.server, self.channel)
        if self.xchat_context:
            artist = self.shell.props.db.entry_get(entry, rhythmdb.PROP_ARTIST)
            title = self.shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
            album = self.shell.props.db.entry_get(entry, rhythmdb.PROP_ALBUM)
            xchat.SetContext(self.xchat_context)
            xchat.Command('say Playing: %s - %s (%s)' % (artist, title, album))
            if not self.xchat_hook:
                self.xchat_hook = xchat.HookPrint('Channel Message', 0, 0)
                self.signal = self.bus.add_signal_receiver(
                    self.got_message,
                    'PrintSignal',
                    'org.xchat.plugin',
                    'org.xchat.service',
                    '/org/xchat/Remote'
                )
        elif self.xchat_hook:
            self.signal.remove()
            xchat.Unhook(self.xchat_hook)
            self.xchat_hook = None
    
    def got_message(self, data, priority, context):
        if context == self.xchat_context:
            msg = str(data[1])
            if msg == 'next':
                self.player.do_next()
    
    def create_configure_dialog(self, dialog=None):
        if not dialog:
            builder_file = self.find_file('conf.ui')
            dialog = ConfDialog(builder_file).dialog
        dialog.present()
        return dialog

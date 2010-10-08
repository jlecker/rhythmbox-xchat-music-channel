import rb
import rhythmdb
import dbus

from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)


class MwcDevsMusicPlugin(rb.Plugin):
    def activate(self, shell):
        self.shell = shell
        self.player = shell.get_player()
        
        self.bus = dbus.SessionBus()
        self.xchat_object = self.bus.get_object('org.xchat.service', '/org/xchat/Remote')
        xchat = dbus.Interface(self.xchat_object, 'org.xchat.plugin')
        self.xchat_hook = xchat.HookPrint('Channel Message', 0, 0)
        self.xchat_context = int(xchat.FindContext('irc.freenode.net', '##rb_music_channel'))
        
        self.event_id = self.player.connect('playing-song-changed', self.song_changed)
        self.bus.add_signal_receiver(
            self.got_message,
            'PrintSignal',
            'org.xchat.plugin',
            'org.xchat.service',
            '/org/xchat/Remote'
        )
    
    def deactivate(self, shell):
        self.bus.remove_signal_receiver(
            self.got_message,
            'PrintSignal',
            'org.xchat.plugin',
            'org.xchat.service',
            '/org/xchat/Remote'
        )
        self.player.disconnect(self.event_id)
        xchat = dbus.Interface(self.xchat_object, 'org.xchat.plugin')
        xchat.Unhook(self.xchat_hook)
        del self.event_id
        del self.xchat_context
        del self.xchat_hook
        del self.xchat_object
        del self.bus
        del self.player
        del self.shell
    
    def song_changed(self, player, entry):
        artist = self.shell.props.db.entry_get(entry, rhythmdb.PROP_ARTIST)
        title = self.shell.props.db.entry_get(entry, rhythmdb.PROP_TITLE)
        album = self.shell.props.db.entry_get(entry, rhythmdb.PROP_ALBUM)
        
        xchat = dbus.Interface(self.xchat_object, 'org.xchat.plugin')
        xchat.SetContext(self.xchat_context)
        xchat.Command('say Playing: %s - %s (%s)' % (artist, title, album))
    
    def got_message(self, data, priority, context):
        if int(context) == self.xchat_context:
            msg = str(data[1])
            if msg == 'next':
                self.player.do_next()
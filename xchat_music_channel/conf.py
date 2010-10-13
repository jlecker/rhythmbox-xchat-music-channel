import gtk
import gconf


gconf_keys = {
    'server': '/apps/rhythmbox/plugins/xchat_music_channel/server',
    'channel': '/apps/rhythmbox/plugins/xchat_music_channel/channel',
}

class ConfDialog(object):
    def __init__(self, builder_file):
        self.gconf = gconf.client_get_default()
        builder = gtk.Builder()
        builder.add_from_file(builder_file)
        self.dialog = builder.get_object('prefs_dialog')
        
        self.server_entry = builder.get_object('server_entry')
        server = self.gconf.get_string(gconf_keys['server'])
        if server is None:
            server = 'irc.freenode.net'
        self.server_entry.set_text(server)
        
        self.channel_entry = builder.get_object('channel_entry')
        channel = self.gconf.get_string(gconf_keys['channel'])
        if channel is None:
            channel = '##rhythmbox_xchat_music_channel'
        self.channel_entry.set_text(channel)
        self.dialog.connect('response', self.response)
    
    def response(self, dialog, response):
        self.gconf.set_string(gconf_keys['server'], self.server_entry.get_text())
        self.gconf.set_string(gconf_keys['channel'], self.channel_entry.get_text())
        self.dialog.hide()
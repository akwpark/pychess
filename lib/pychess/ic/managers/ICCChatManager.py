from gi.repository import GLib, GObject

from pychess.ic import GAME_TYPES
from pychess.ic.icc import DG_PLAYERS_IN_MY_GAME, DG_KIBITZ
from pychess.ic.managers.ChatManager import ChatManager


class ICCChatManager(ChatManager):
    def __init__(self, connection):
        GObject.GObject.__init__(self)
        self.connection = connection

        self.connection.expect_dg_line(DG_PLAYERS_IN_MY_GAME, self.on_icc_players_in_my_game)
        self.connection.expect_dg_line(DG_KIBITZ, self.on_icc_kibitz)

        self.connection.client.run_command("set-2 %s 1" % DG_PLAYERS_IN_MY_GAME)
        self.connection.client.run_command("set-2 %s 1" % DG_KIBITZ)

        self.currentLogChannel = None

        self.connection.client.run_command("set Lang English")

        self.connection.client.run_command("set height 240")

        self.connection.client.run_command("inchannel %s" %
                                           self.connection.username)
        self.connection.client.run_command("help channel_list")
        self.channels = {}
        self.observers = {}

    def on_icc_players_in_my_game(self, data):
        # gamenumber playername symbol kibvalue
        # O=observing
        # PW=playing white
        # PB=playing black
        # SW=playing simul and is white
        # SB=playing simul and is black
        # E=Examining
        # X=None (has left the table)

        gameno, name, symbol, kibvalue = data.split()

        ficsplayer = self.connection.players.get(name)
        rating = ficsplayer.getRatingByGameType(GAME_TYPES['standard'])
        if rating:
            name = "%s(%s)" % (name, rating)

        if gameno not in self.observers:
            observers = set()
            self.observers[gameno] = observers

        if symbol == "O":
            self.observers[gameno].add(name)
        elif symbol == "X" and name in self.observers[gameno]:
            self.observers[gameno].remove(name)

        obs_str = " ".join(list(self.observers[gameno]))
        self.emit('observers_received', gameno, obs_str)

    def on_icc_kibitz(self, data):
        # gamenumber playername titles kib/whi ^Y{kib string^Y}
        gameno, name, rest = data.split(" ", 2)
        titles, rest = rest.split("}", 1)
        kib_whi, text = rest[1:].split(" ", 1)
        text = text[2:-2]

        if kib_whi == "1":
            GLib.idle_add(self.emit, "kibitzMessage", name, int(gameno), text)
        else:
            GLib.idle_add(self.emit, "whisperMessage", name, int(gameno), text)

# -*- coding: UTF-8 -*-
from __future__ import print_function

import os

from gi.repository import Gtk, GObject
from gi.repository.GdkPixbuf import Pixbuf

from pychess.perspectives import perspective_manager
from pychess.Utils.IconLoader import load_icon
from pychess.Savers.database import Database
from pychess.widgets import gamewidget

pdb_icon = load_icon(32, "pychess")
pgn_icon = load_icon(32, "application-x-chess-pgn", "pychess")
CLIPBASE = "Clipbase"


class SwitcherPanel(Gtk.IconView):
    __gsignals__ = {
        'chessfile_switched': (GObject.SignalFlags.RUN_FIRST, None, (object, )),
    }

    def __init__(self, gamelist):
        GObject.GObject.__init__(self)
        self.gamelist = gamelist
        self.widgets = gamewidget.getWidgets()

        self.persp = perspective_manager.get_perspective("database")
        self.persp.connect("chessfile_opened", self.on_chessfile_opened)
        self.persp.connect("chessfile_closed", self.on_chessfile_closed)
        self.persp.connect("chessfile_imported", self.on_chessfile_imported)

        self.alignment = Gtk.Alignment()

        self.liststore = Gtk.ListStore(object, Pixbuf, str)
        self.set_model(self.liststore)
        self.set_pixbuf_column(1)
        self.set_text_column(2)
        self.set_item_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_activate_on_single_click(True)
        self.set_selection_mode(Gtk.SelectionMode.BROWSE)

        pixbuf = Gtk.IconTheme.get_default().load_icon("edit-paste", 32, 0)
        info = "%s\n%s  %s" % (CLIPBASE, "pdb", 0)
        self.liststore.append([self.gamelist.chessfile, pixbuf, info])

        self.connect("item-activated", self.on_item_activated)

        self.alignment.add(self)
        self.alignment.show_all()

        treepath = Gtk.TreePath(0)
        self.select_path(treepath)

    def set_sensitives(self, chessfile):
        if isinstance(chessfile, Database):
            self.persp.import_button.set_sensitive(True)
            self.widgets["import_chessfile"].set_sensitive(True)
            self.widgets["import_endgame_nl"].set_sensitive(True)
            self.widgets["import_twic"].set_sensitive(True)
            self.widgets["update_players"].set_sensitive(True)
        else:
            self.persp.import_button.set_sensitive(False)
            self.widgets["import_chessfile"].set_sensitive(False)
            self.widgets["import_endgame_nl"].set_sensitive(False)
            self.widgets["import_twic"].set_sensitive(False)
            self.widgets["update_players"].set_sensitive(False)

    def on_item_activated(self, iconview, path):
        treeiter = self.liststore.get_iter(path)
        chessfile = self.liststore.get_value(treeiter, 0)
        self.gamelist.chessfile = chessfile
        self.gamelist.offset = 0
        self.gamelist.chessfile.build_query()
        self.gamelist.load_games()

        self.set_sensitives(chessfile)

        self.emit("chessfile_switched", chessfile)

    def on_chessfile_opened(self, persp, chessfile):
        name, ext = os.path.splitext(chessfile.path)
        icon = pgn_icon if ext.lower() == ".pgn" else pdb_icon
        # basename = os.path.basename(name)
        info = "%s\n%s  %s" % (name, ext[1:], chessfile.count)
        treeiter = self.liststore.append([chessfile, icon, info])
        treepath = self.liststore.get_path(treeiter)
        self.select_path(treepath)

        self.set_sensitives(chessfile)

    def on_chessfile_closed(self, persp):
        if self.gamelist.chessfile.path is not None:
            for i, row in enumerate(self.liststore):
                if row[0] == self.gamelist.chessfile:
                    # print("removing %s" % self.gamelist.chessfile.path)
                    # first remove the closed
                    treeiter = self.liststore.get_iter(Gtk.TreePath(i))
                    self.liststore.remove(treeiter)

                    # then select the previous
                    treepath = Gtk.TreePath(i - 1)
                    self.select_path(treepath)
                    self.item_activated(treepath)
                    self.queue_draw()
                    break
        else:
            self.set_sensitives(None)

    def on_chessfile_imported(self, persp, chessfile):
        if chessfile.path is None:
            info = "%s\n%s  %s" % (CLIPBASE, "pdb", chessfile.count)
        else:
            name, ext = os.path.splitext(chessfile.path)
            # basename = os.path.basename(name)
            info = "%s\n%s  %s" % (name, ext[1:], chessfile.count)

        for i, row in enumerate(self.liststore):
            if row[0] == self.gamelist.chessfile:
                treeiter = self.liststore.get_iter(Gtk.TreePath(i))
                self.liststore[treeiter][2] = info
                break

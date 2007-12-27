#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['DateButton']

import gtk
import gobject
import time
import datetime

from lib import i18n

class DateButton(gtk.Button):
    def __init__(self, parent=None):
        gtk.Button.__init__(self)
        self.parent_window = parent
        #TRANSLATORS: No date selected
        self.set_label(_("None"))
        self.date = None

        self.connect("clicked", self.show_calendar)

    def set_date(self, int):
        self.set_label(_("None"))

    def show_calendar(self, *arg):
        dialog = gtk.Dialog(title=_("Select date and hour"),
                            parent=self.parent_window,
                            flags=gtk.DIALOG_MODAL,
                            buttons=("None", gtk.RESPONSE_REJECT,
                                     gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT))

        if self.parent_window:
            dialog.set_transient_for(self.parent_window)
            dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        table = gtk.Table(rows=2, columns=3, homogeneous=False)
        calendar = gtk.Calendar()

        table.attach(calendar, 0, 3, 0, 1, gtk.FILL, gtk.FILL)
        dialog.vbox.pack_start(table, expand=False, fill=True, padding=10)

        dialog.show_all()

        dialog.run()

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

    def set_date(self, date):
        if not date:
            self.date = None
            self.set_label(_("None"))
            return

        (year, month, day, hour, minute) = date
        # Create datetime object
        selectedDate = datetime.datetime(year, month, day, hour, minute)
        # Turn it into a time object
        self.date = time.mktime(selectedDate.timetuple())
        self.set_label(selectedDate.strftime(_('%Y/%m/%d %H:%M').encode('ASCII')))

    def show_calendar(self, *arg):
        dialog = gtk.Dialog(title=_("Select date and hour"),
                            parent=self.parent_window,
                            flags=gtk.DIALOG_MODAL,
                            buttons=(str(_("None")), gtk.RESPONSE_REJECT,
                                     gtk.STOCK_OK, gtk.RESPONSE_OK))

        if self.parent_window:
            dialog.set_transient_for(self.parent_window)
            dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        table = gtk.Table(rows=2, columns=3, homogeneous=False)
        calendar = gtk.Calendar()

        table.attach(calendar, 0, 3, 0, 1, gtk.FILL, gtk.FILL)
        dialog.vbox.pack_start(table, expand=False, fill=True, padding=10)

        dialog.show_all()

        response = dialog.run()
        print response
        if response == gtk.RESPONSE_REJECT:
            self.set_date(None)
        elif response == gtk.RESPONSE_OK:
            # Extracts the date off the calendar widget
            day = calendar.get_date()[2]
            month = calendar.get_date()[1] + 1
            year = calendar.get_date()[0]
            hour = 5
            minute = 0
            self.set_date((year, month, day, hour, minute))

        dialog.destroy()

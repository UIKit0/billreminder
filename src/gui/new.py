#!/usr/bin/env python
# - coding: utf-8 -

import gtk
from db import entities
from lib import utils
import widgets

import datetime as dt

TODAY = dt.date.today()
NEXT_WEEK = TODAY + dt.timedelta(days=7)
LAST_WEEK = TODAY - dt.timedelta(days=7)

class MainWindow:
    def __init__(self):
        # Create a new window
        self.ui = utils.load_ui_file("new.ui")
        self.window = self.ui.get_object("main_window")

        self.upcoming = widgets.BillTree()
        self.ui.get_object("bill_box").add(self.upcoming)

        self.window.show_all()
        self.ui.connect_signals(self)

        self.load_bills()

    def load_bills(self):
        self.upcoming.clear()

        ht = entities.Bill('Harris Teeter', 123.94, TODAY)
        food = entities.Category('Groceries', '#ad7fa8')
        ht.category = food

        aes = entities.Bill('Alan & Sons', 41.65, NEXT_WEEK)
        dining = entities.Category('Dining', '#fce94f')
        aes.category = dining

        energy = entities.Bill('Duke Energy', 62, LAST_WEEK)
        utilities = entities.Category('Utilities', '#73d216')
        energy.category = utilities

        self.upcoming.add_bill(ht)
        self.upcoming.add_bill(aes)
        self.upcoming.add_bill(energy)


    # close the window and quit
    def on_delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False


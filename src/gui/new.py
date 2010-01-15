#!/usr/bin/env python
# - coding: utf-8 -

import gtk
from db import entities
from lib import utils
import widgets

import datetime as dt

class MainWindow:
    def __init__(self):
        # Create a new window
        self.ui = utils.load_ui_file("new.ui")
        self.window = self.ui.get_object("main_window")

        self.upcoming = widgets.BillTree()
        self.ui.get_object("upcoming_box").add(self.upcoming)

        self.window.show_all()
        self.ui.connect_signals(self)
        
        self.load_bills()

    def load_bills(self):
        self.upcoming.clear()

        ht = entities.Bill('Harris Teeter', 123.94, dt.date.today())
        food = entities.Category('Groceries')
        ht.category = food

        self.upcoming.add_bill(ht)
        

    # close the window and quit
    def on_delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False


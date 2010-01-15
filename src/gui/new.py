#!/usr/bin/env python
# - coding: utf-8 -

import gtk
from db import entities
from gui import widgets

class BasicWindow:

    # close the window and quit
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def __init__(self):
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_title("Basic Window")

        self.window.set_size_request(300, 200)

        self.window.connect("delete_event", self.delete_event)

        from datetime import date
        dt = date.today()
        ht = entities.Bill('Harris Teeter', 123.94, dt)
        food = entities.Category('Groceries')
        ht.category = food

        bt = widgets.BillTree()
        bt.add_bill(ht)

        self.window.add(bt)
        self.window.show_all()

def main():
    gtk.main()

if __name__ == "__main__":
    example = BasicWindow()
    main()

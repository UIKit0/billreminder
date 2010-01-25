#!/usr/bin/env python
# - coding: utf-8 -

import gtk
from db import entities
from lib import dialogs
from lib import utils
import widgets

from lib.actions import Actions # data model
from widgets import charting

import itertools

import datetime as dt
import calendar

(PAID, UPCOMING, OVERDUE) = range(3)

class MainWindow:
    def __init__(self):
        # Create a new window
        self.ui = utils.load_ui_file("new.ui")
        self.window = self.ui.get_object("main_window")
        self.actions = Actions()

        self.upcoming = widgets.BillTree()
        self.ui.get_object("bill_box").add(self.upcoming)

        today = dt.date.today()
        self.start_date = today - dt.timedelta(today.day - 1) # beginning of month
        first_weekday, days_in_month = calendar.monthrange(today.year, today.month)
        self.end_date = self.start_date + dt.timedelta(days_in_month - 1)

        self.filtered_types = []
        self.filtered_categories = []

        self.time_chart = widgets.TimeChart()
        self.get_widget("time_box").add(self.time_chart)
        self.time_chart.connect('motion-notify-event', self.on_time_chart_motion)
        self.time_chart.connect('button-press-event', self.on_time_chart_press)
        self.time_chart.connect('button-release-event', self.on_time_chart_release)
        self.time_chart.connect('scroll-event', self.on_time_chart_scroll)
        self.__time_chart_pressed = False

        self.type_chart = charting.HorizontalBarChart(interactive = True)
        self.type_chart.max_bar_width = 20
        self.type_chart.legend_width = 60
        self.type_chart.connect("bar-clicked", self.on_type_chart_clicked)
        self.get_widget("by_type").add(self.type_chart)

        self.category_chart = charting.HorizontalBarChart(interactive = True)
        self.category_chart.max_bar_width = 20
        self.category_chart.legend_width = 60
        self.category_chart.connect("bar-clicked", self.on_category_chart_clicked)
        self.get_widget("by_category").add(self.category_chart)

        self.load_bills()
        self.ui.connect_signals(self)
        self.window.show_all()

    def load_bills(self):
        self.set_title()
        self.upcoming.clear()

        start_date, end_date = self.start_date, self.end_date
        paid = None

        if PAID in self.filtered_types: # paid
            paid = True

        if UPCOMING in self.filtered_types: # upcoming
            # Make sure to show upcoming bills for the selected month only.
            start_date = max(self.start_date, dt.date.today() + dt.timedelta(days = 1))

        if OVERDUE in self.filtered_types: # overdue
            end_date = dt.date.today() - dt.timedelta(days = 1)

        bills = self.actions.get_interval_bills(start_date, end_date, paid)
        for bill in bills:
            self.upcoming.add_bill(bill)

        self.update_graphs(bills)

    def on_type_chart_clicked(self, area, idx):
        if idx in self.filtered_types:
            self.type_chart.bars_selected.remove(idx)
            self.filtered_types.remove(idx)
        else:
            self.type_chart.bars_selected.append(idx)
            self.filtered_types.append(idx)
        self.load_bills()


    def on_category_chart_clicked(self, area, idx):
        if idx in self.filtered_categories:
            self.category_chart.bars_selected.remove(idx)
            self.filtered_categories.remove(idx)
        else:
            self.category_chart.bars_selected.append(idx)
            self.filtered_categories.append(idx)
        self.load_bills()

    def set_title(self):
        if (self.start_date.month == self.end_date.month and self.start_date.year == self.end_date.year):
            title = "%s - %s" % (self.start_date.strftime("%B %d"),
                                self.end_date.strftime("%d, %Y"))
        elif (self.start_date.year == self.end_date.year):
            title = "%s - %s" % (self.start_date.strftime("%B %d"),
                                self.end_date.strftime("%B %d, %Y"))
        else:
            title = "%s - %s" % (self.start_date.strftime("%B %d %Y"),
                                self.end_date.strftime("%B %d %Y"))

        self.get_widget("range_title").set_text(title)


    def update_graphs(self, bills):
        bill_amounts = [(bill.dueDate, float(bill.amount)) for bill in bills]
        self.time_chart.draw(bill_amounts, self.start_date, self.end_date)


        today = dt.date.today()
        # totals by type - paid, upcoming and overdue
        bill_types = (_("Paid"), _("Upcoming"), _("Overdue"))
        type_totals = [0,0,0]
        for bill in bills:
            if bill.paid:
                type_totals[0] += float(bill.amount)
            elif bill.dueDate > today: # upcoming
                type_totals[1] += float(bill.amount)
            else: # overdue
                type_totals[2] += float(bill.amount)
        self.type_chart.plot(bill_types, type_totals)



        # totals by category
        bills = sorted(bills, key=lambda bill: bill.category.name)
        category_keys = []
        category_amount = []
        for category, totals in itertools.groupby(bills, lambda bill: bill.category):
            total_amount = sum([float(total.amount) for total in totals])
            category_keys.append(category.name)
            category_amount.append(total_amount)

        self.category_chart.plot(category_keys, category_amount)


    def on_prev_clicked(self, button):
        self.end_date = self.start_date - dt.timedelta(1)
        first_weekday, days_in_month = calendar.monthrange(self.end_date.year, self.end_date.month)
        self.start_date = self.end_date - dt.timedelta(days_in_month - 1)
        self.load_bills()

    def on_next_clicked(self, button):
        self.start_date = self.end_date + dt.timedelta(1)
        first_weekday, days_in_month = calendar.monthrange(self.start_date.year, self.start_date.month)
        self.end_date = self.start_date + dt.timedelta(days_in_month - 1)
        self.load_bills()

    def on_home_clicked(self, button):
        today = dt.date.today()
        self.start_date = today - dt.timedelta(today.day - 1) #set to beginning of month
        first_weekday, days_in_month = calendar.monthrange(today.year, today.month)
        self.end_date = self.start_date + dt.timedelta(days_in_month - 1)

        self.load_bills()

    def on_new_clicked(self, button):
        today = dt.date.today()
        records = dialogs.add_dialog(parent=self.window, selectedDate=today)

        # Checks if the user did not cancel the action
        if records:
            # Add new bill to database
            for rec in records:
                bill = self.actions.add(rec)
                if bill:
                    self.upcoming.add_bill(bill)
        self.load_bills()

    def on_edit_clicked(self, button):
        current = self.upcoming.get_selected_bill()
        if not current:
            return

        records = dialogs.edit_dialog(parent=self.window, record=current)

        # Checks if the user did not cancel the action
        if records:
            for rec in records:
                # Edit bill to database
                rec = self.actions.edit(rec)
        self.load_bills()

    def on_delete_clicked(self, button):
        current = self.upcoming.get_selected_bill()
        if not current:
            return

        message = utils.Message()
        resp = message.ShowQuestionYesNo(
            _("Do you really want to delete \"%s\"?") % \
            current.payee,
            self.window, _("Confirmation"))
        if not resp:
            return

        self.actions.delete(current)
        self.load_bills()

    def on_time_chart_motion(self, widget, event):
        if self.__time_chart_pressed is not False:
            width = widget.get_allocation().width
            days = (event.x - self.__time_chart_pressed['x']) / (width / (self.__time_chart_pressed['end_date'] - self.__time_chart_pressed['start_date']).days)

            self.start_date = self.__time_chart_pressed['start_date'] - dt.timedelta(days=days)
            self.end_date = self.__time_chart_pressed['end_date'] - dt.timedelta(days=days)
            self.load_bills()

    def on_time_chart_press(self, widget, event):
        self.__time_chart_pressed = {'x': event.x,
            'start_date': self.start_date,
            'end_date': self.end_date}
        widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.FLEUR))

    def on_time_chart_release(self, widget, event):
        self.__time_chart_pressed = False
        widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.ARROW))

    def on_time_chart_scroll(self, widget, event):
        if event.direction in (gtk.gdk.SCROLL_DOWN, gtk.gdk.SCROLL_RIGHT):
            self.start_date = self.start_date + dt.timedelta(days=1)
            self.end_date = self.end_date + dt.timedelta(days=1)
            self.load_bills()
        else:
            self.start_date = self.start_date - dt.timedelta(days=1)
            self.end_date = self.end_date - dt.timedelta(days=1)
            self.load_bills()

    def on_about_clicked(self, button):
        dialogs.about_dialog(parent=self.window)

    def get_widget(self, name):
        """ skip one variable (huh) """
        return self.ui.get_object(name)

    # close the window and quit
    def on_delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

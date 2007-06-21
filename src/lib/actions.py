#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import dal
import bill
from lib import common
from lib.utils import force_string
from db.billstable import BillsTable

class Actions(object):

    def __init__(self, databaselayer=None):
        if not databaselayer:
            databaselayer = dal.DAL()
        
        self.dal = databaselayer

    def get_bills(self, kwargs):
        """ Returns one or more records that meet the criteria passed """
        return self.dal.get(BillsTable, kwargs)

    def add_bill(self, kwargs):
        """ Adds a bill to the database """
        return self.dal.add(BillsTable, kwargs)

    def edit_bill(self, kwargs):
        """ Edit a record in the database """
        return self.dal.edit(BillsTable, kwargs)

    def delete_bill(self, key):
        """ Delete a record in the database """
        return self.dal.delete(BillsTable, key)

if not '--standalone' in sys.argv and not 'billreminderd' in sys.argv:
    from lib.dbus_actions import Actions


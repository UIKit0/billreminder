#!/usr/bin/python
# -*- coding: utf-8 -*-

import dal
import bill

class Actions(object):

    def __init__(self, databaselayer=None):
        if not databaselayer:
            databaselayer = dal.DAL()

        self.dal = databaselayer

    def add_bill(self, bill):
        """ Adds a bill to the database """
        # Turn it into a dictionary
        billdict = bill.Dictionary
        # Remove the Id field
        billdict.pop('Id')
        # Separate columns and values
        values = billdict.values()
        cols = billdict.keys()
        # Insert statement
        stmt = "INSERT INTO %s (%s) VALUES (%s)" % \
            ('br_BillsTable', ",".join(cols), ",".join('?' * len(values)))

        try:
            # Execute it
            self.dal.cur.execute(stmt, values)
            # Grab the Id for the last record entered
            id = self.dal.cur.lastrowid
            # Return it
            bill.Id = id

            return bill
        except Exception, e:
            print str(e)
            return None

    def edit_bill(self, key, dic):
        """ Edit a record in the database """
        # Removes the key field
        if self.dal.tables[tblnick].KeyAuto:
            del dic[self.dal.tables[tblnick].Key]
        
        # Split up into pairs
        pairs = dic.items()
        
        params = "=?, ".join([ x[0] for x in pairs ]) + "=?"
        stmt = "UPDATE %s SET %s WHERE %s=?" \
            % (self.dal.tables[tblnick].Name, params, self.dal.tables[tblnick].Key)
        
        args = [x[1] for x in pairs] + [key]
        
        rowsAffected = self.dal._executeSQL(stmt, args)
        return rowsAffected

    def delete_bill(self, tblnick, key):
        """ Delete a record in the database """
        # Delete statement
        stmt = "DELETE FROM %s WHERE %s=?" % (self.dal.tables[tblnick].Name, self.dal.tables[tblnick].Key)
        try:
            self.dal._executeSQL(stmt, [key])
            return True
        except Exception, e:
            # Dump error to the screen; may be helpfull when debugging
            print str(e)
            return False

#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ['DAL']

import os, sys

try:
    from pysqlite2 import dbapi2 as sqlite
except ImportError:
    print "Please install pysqlite2"
    sys.exit(1)

from lib.bill import Bill
from db.versionstable import VersionsTable
from db.configtable import ConfigTable
from db.fieldstable import FieldsTable
from db.billstable import BillsTable

class DAL(object):

    # Database name and path
    dbName = 'billreminder.db'
    dbPath = '%s/.config/billreminder/data/' % os.environ['HOME']

    # Tables used by applications and corresponding versions
    tables = {'tblversions': VersionsTable(),
        'tblconfig': ConfigTable(),
        'tblfields': FieldsTable(),
        'tblbills': BillsTable()}
    # Same dict, but with real table name 
    _tables = dict([(tables[table].Name, tables[table]) for table in tables])
    _nicks = dict([(tables[table].Name, table) for table in tables])

    def __init__(self):
        if not os.path.isdir(self.dbPath):
            os.makedirs(self.dbPath)

        self.conn = sqlite.connect(os.path.join(self.dbPath, self.dbName), isolation_level=None)
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA count_changes=0")

        if os.path.isfile(os.path.join(self.dbPath, self.dbName)):
            self.validateTables()
        else:
            self._createDb()

    def _createDb(self):
        """ All tables get created here."""
        # First, we create them
        for table in self.tables.values():
            self._createTable(table.Name)

        # Now save their field info
        for table in self.tables.values():
            self._updateFieldsInformation(table.Name)

        # Now save their version info
        for table in self.tables.values():
            self.update_tableVersion(table.Name)


    def _createTable(self, tblname):
        # Create the table
        self.cur.execute(self._tables[tblname].CreateSQL)
        self.conn.commit()
        print tblname

    def _updateFieldsInformation(self, tblname):
        """ Adds field information for every table."""
        # Saves fields information for every table except tblfields
        self.add('tblfields', {'tablename': tblname, 'fields': ", ".join(self._tables[tblname].Fields)})

    def update_tableVersion(self, tblname):
        """ Adds table verison information."""
        # Save version information for every table
        self.add('tblversions', {'tablename': tblname, 'version': self._tables[tblname].Version})
        print 'version saved (%s - %i)' % (tblname, self._tables[tblname].Version)

    def validateTables(self):
        """ Validates that all tables are up to date. """
        stmt = "select tbl_name from sqlite_master where type = 'table' and tbl_name like 'br_%'"
        self.cur.execute(stmt)
        # List of all tables with names that start with "br_"
        tbllist = self.cur.fetchall()
        print tbllist

        # Create all tables if database is empty
        if len(tbllist) == 0: 
            self._createDb()
            return True

        unvalidated = self._tables.copy()
        #unvalidated.pop(self.tables['tblversions'].Name)
        #unvalidated.pop(self.tables['tblfields'].Name)
        for tblname in tbllist:
            tblname = str(tblname[0])
            try:
                #ver = self.get('tblversions', {'tablename': tblname})[0]['version']
                ver = self.get(VersionsTable, {'tablename': tblname})[0]['version']
            except sqlite.OperationalError:
                ver = -1
            print ver
            # Table is obsolete and will be deleted 
            if tblname not in self._tables:
                # We should revisit this logic
                print  '%s is an obsolete table and it will be deleted' % tblname
                self._delete_table(tblname)
                continue
            if self._tables[tblname].Version == int(ver) :
                print '%s is a valid table' % tblname
            else:
                print '%s is NOT a valid table' % tblname
                self._update_table(tblname)
            # Remove valid tables from dict
            unvalidated.pop(tblname)

        # Create tables new in actual version
        for table in unvalidated:
            self._createTable(table)

    def _delete_table(self, tblname):
        stmt = "DROP TABLE %s" % tblname
        self.cur.execute(stmt)
        self.delete('tblversions',  tblname)
        print "Removed table %s" % tblname

    def _update_table(self, tblname):
        oldfields = self.get('tblfields', {'tablename': tblname})[0]['fields'].split(', ')
        stmt = "SELECT %(fields)s FROM %(name)s" \
            % dict(fields=", ".join(oldfields), name=tblname)
        self.cur.execute(stmt)
        oldrecords = [dict([ (f, row[i]) for i, f in enumerate(oldfields) ]) \
            for row in self.cur.fetchall()]
        stmt = "ALTER TABLE %s RENAME TO %s_old" % (tblname, tblname)
        self.cur.execute(stmt)
        self.delete('tblversions',  tblname)
        self.delete('tblfields', tblname)
        self._createTable(tblname)

        for rec in oldrecords:
            self.add(self._nicks[tblname], dict([(col,rec.get(col,'')) for col in self._tables[tblname].Fields]))

        self._delete_table('%s_old' % tblname)

    def _create_query_params(self, kwargs):
        """ Helper method to create a statement and arguments to a query. """
        if None == kwargs or 0 == len(kwargs):
            return ("", [])

        if not isinstance(kwargs,str):
            pairs = kwargs.items()
            stmt = " WHERE " + \
                " AND ".join([ x[0] + (None is x[1] and " IS NULL" or " = ?")
                    for x in pairs ])

            args = [ x[1] for x in filter(lambda x: None is not x[1], pairs) ]
        else:
            stmt = " WHERE " + kwargs
            args = []
        return (stmt, args)

    def edit(self, table, kwargs):
        """ Edit a record in the database """
        # Removes the key field
        key = kwargs[table.Key]
        if table.KeyAuto:
            del kwargs[table.Key]

        # Split up into pairs
        pairs = kwargs.items()

        params = "=?, ".join([ x[0] for x in pairs ]) + "=?"
        stmt = "UPDATE %s SET %s WHERE %s=?" \
            % (table.Name, params, table.Key)

        params = [x[1] for x in pairs] + [key]

        return self._executeSQL(stmt, params)

    def delete(self, table, key):
        """ Delete a record in the database """
        # Delete statement
        stmt = "DELETE FROM %s WHERE %s=?" % (table.Name, table.Key)

        try:
            self._executeSQL(stmt, [key])
            return True
        except Exception, e:
            # Dump error to the screen; may be helpfull when debugging
            print str(e)
            return False

    def add(self, table, kwargs):
        """ Adds a record to the database """

        if table.KeyAuto:
            kwargs.pop(table.Key)
        # Separate columns and values
        values = kwargs.values()
        cols = kwargs.keys()
        # Insert statement
        stmt = "INSERT INTO %s (%s) VALUES (%s)" %\
            (table.Name, ",".join(cols), ",".join('?' * len(values)))
        self.cur.execute(stmt, values)
        b_key = self.cur.lastrowid
        if b_key:
            rows = self.get(table, {table.Key: b_key})
            try: return rows[0]
            except: None

    def get(self, table, kwargs):
        """ Returns one or more records that meet the criteria passed """
        (stmt, args) = self._create_query_params(kwargs)

        stmt = "SELECT %(fields)s FROM %(name)s" \
            % dict(fields=", ".join(table.Fields), name=table.Name) + stmt
        try:
            self.cur.execute(stmt, args)
        except sqlite.OperationalError:
            return None


        rows = [dict([ (f, row[i]) for i, f in enumerate(table.Fields) ]) \
            for row in self.cur.fetchall()]

        return rows

    def _executeSQL(self, stmt, args):
        """ Excutes passed SQL and returns the result """
        try:
            return self.cur.execute(stmt, args)
        except Exception, e:
            print "Unexpected error:", sys.exc_info()[0], e
            return None

#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ['ConfigTable']

from generictable import GenericTable

class ConfigTable(GenericTable):
    """ Table to hold version information for all tables. """
    Version = 1
    Key = "key"
    KeyAuto = False
    Name = "br_ConfigTable"
    CreateSQL = """
        CREATE TABLE %s (
        key  VARCHAR(255) NOT NULL,
        value VARCHAR(255) NOT NULL)
    """ % Name
    Fields = ['key', 'value']

    def __init__(self):
        GenericTable.__init__(self)

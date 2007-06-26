#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ['Config']

import os

from ConfigParser import ConfigParser

class Config(ConfigParser):

    def __init__(self):
        defaults = {}
        ConfigParser.__init__(self, defaults)
        self.filename = os.path.expanduser('~/.config/billreminder/billreminder.cfg')
        self.read(['default.cfg', self.filename])

    def reload(self):
        self.read(['default.cfg', self.filename])

    def save(self):
        file = open(self.filename, 'w')
        self.write(file)

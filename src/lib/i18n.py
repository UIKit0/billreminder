#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['_', 'N_']

program = 'billreminder'

import locale
LC_ALL = locale.setlocale(locale.LC_ALL, '') 

try:
    import gettext
    from gettext import gettext as _, ngettext as N_
    gettext.install(program, unicode=True)
    import __builtin__
    __builtin__.__dict__['N_'] = N_
except ImportError:
    import sys
    print >> sys.stderr, ("You don't have gettext module, no " \
                          "internationalization will be used.")
    import __builtin__
    __builtin__.__dict__['_'] = lambda x: x
    __builtin__.__dict__['N_'] = lambda x, y, n: (n == 1) and x or y

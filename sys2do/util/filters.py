# -*- coding: utf-8 -*-
'''
###########################################
#  Created on 2011-10-25
#  @author: cl.lam
#  Description:
###########################################
'''
import datetime
from itertools import imap, ifilter
from jinja2.filters import do_default


__all__ = ['ft', 'fd', 'fn', 'ifFalse', 'f', ]


SYSTEM_DATE_FORMAT = "%Y-%m-%d"
SYSTEM_TIME_FORMAT = "%H:%M"
SYSTEM_DATETIME_FORMAT = "%Y-%m-%d %H:%M"

def ft(t, f = SYSTEM_DATETIME_FORMAT):
    try:
        return t.strftime(f)
    except:
        return '' if not t else str(t)


def fd(d, f = SYSTEM_DATE_FORMAT):
    try:
        return d.strftime(f)
    except:
        return '' if not d else str(d)


def fn(d, f = '%.2f'): return f % (d or 0)


def ifFalse(v, default = u""):
    return do_default(v, default) or default


f = ifFalse

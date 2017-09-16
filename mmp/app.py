"""The wx app."""

import os
import os.path
import wx
from jinja2 import Environment

running = True  # Set to False when we close.
app = wx.App(False)

frame = None  # The main frame.
lyrics_frame = None
track_format_template = None
title_template = None

name = 'MMP'
version = '0.1Pre'
description = 'The multitool of media players.'

authors = (
    'Chris Norman',
)

app.SetAppName(name)

paths = wx.StandardPaths.Get()

data_dir = paths.GetUserDataDir()
media_dir = paths.GetUserLocalDataDir()

for path in [data_dir, media_dir]:
    if not os.path.isdir(path):
        os.makedirs(path)


environment = Environment()


def format_timedelta(td):
    """Format timedelta td."""
    fmt = []  # The format as a list.
    seconds = td.total_seconds()
    years, seconds = divmod(seconds, 31536000)
    if years:
        fmt.append('%d %s' % (years, 'year' if years == 1 else 'years'))
    months, seconds = divmod(seconds, 2592000)
    if months:
        fmt.append('%d %s' % (months, 'month' if months == 1 else 'months'))
    days, seconds = divmod(seconds, 86400)
    if days:
        fmt.append('%d %s' % (days, 'day' if days == 1 else 'days'))
    hours, seconds = divmod(seconds, 3600)
    if hours:
        fmt.append('%d %s' % (hours, 'hour' if hours == 1 else 'hours'))
    minutes, seconds = divmod(seconds, 60)
    if minutes:
        fmt.append(
            '%d %s' % (
                minutes,
                'minute' if minutes == 1 else 'minutes'
            )
        )
    if seconds:
        fmt.append('%.2f seconds' % seconds)
    return english_list(fmt)


def pluralise(n, singular, plural=None):
    """Return singular if n == 1 else plural."""
    if plural is None:
        plural = singular + 's'
    return singular if n == 1 else plural


def english_list(
    l,
    empty='nothing',
    key=str,
    sep=', ',
    and_='and '
):
    """Return a decently-formatted list."""
    l = [key(x) for x in l]
    if not l:
        return empty
    elif len(l) == 1:
        return l[0]
    else:
        res = ''
        for pos, item in enumerate(l):
            if pos == len(l) - 1:
                res += '%s%s' % (sep, and_)
            elif res:
                res += sep
            res += item
        return res


for func in (format_timedelta, english_list, pluralise):
    environment.filters[func.__name__] = func

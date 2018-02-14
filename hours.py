#!/usr/bin/env python3

from datetime import date, timedelta
import re
import sys


DATE_PATTERN = re.compile(r'^\d\d\d\d-\d\d-\d\d$')


HOURS_PATTERN = re.compile(r'^(\d+[,.])?\d+$')


TODAY = date.today()


WEEK_START = TODAY - timedelta(days=TODAY.weekday())


DAYS = {day: WEEK_START + timedelta(days=week_index) for week_index, day in enumerate(('monday',
                                                                                       'tuesday',
                                                                                       'wednesday',
                                                                                       'thursday',
                                                                                       'friday',
                                                                                       'saturday',
                                                                                       'sunday'))}
DAYS.update(today=TODAY,
            yesterday=TODAY - timedelta(days=1),
            tomorrow=TODAY + timedelta(days=1))


def log_hours(name, day, hours):
    print('log', name, day.isoformat(), hours)


def show_day(day):
    pass


def show_range(start, end):
    pass


def do_log(arguments):
    print('log', *arguments)


def do_show(arguments):
    print('show', *arguments)


def main(arguments):
    actions = {
        'log': do_log,
        'show': do_show,
    }

    action = 'log'
    if arguments[0] in actions:
        action = arguments.pop(0)

    actions[action](arguments)


if __name__ == '__main__':
    main(sys.argv[1:])
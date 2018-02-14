#!/usr/bin/env python3

from datetime import date, timedelta
from os import path
import re
import sqlite3
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


DB_FILE = path.expanduser('~/.hours.db')


def ensure_db(database):
    database.execute(
        """
            CREATE TABLE IF NOT EXISTS hours (
                name TEXT,
                day DATE,
                hours REAL
            )
        """
    )
    database.execute(
        """
            CREATE INDEX IF NOT EXISTS days ON hours ( day )
        """
    )


def log_hours(database, name, day, hours):
    database.execute(
        """
            INSERT INTO hours (name, day, hours) VALUES (?, ?, ?)
        """,
        (name, day, hours)
    )


def do_log(database, arguments):
    assert 2 <= len(arguments) <= 3
    day = TODAY
    name = hours = None

    for argument in arguments:
        if argument in DAYS:
            day = DAYS[argument]
        elif DATE_PATTERN.match(argument):
            year, month, day = argument.split('-')
            day = date(int(year), int(month), int(day))
        elif HOURS_PATTERN.match(argument):
            hours = float(argument.replace(',', '.'))
        else:
            name = argument

    assert None not in (name, day, hours)

    log_hours(database, name, day, hours)


def show_day(database, day):
    pass


def show_range(database, start, end):
    pass


def do_show(database, arguments):
    print('show', *arguments)


def main(arguments):
    actions = {
        'log': do_log,
        'show': do_show,
    }

    action = 'log'
    if arguments[0] in actions:
        action = arguments.pop(0)

    with sqlite3.connect(DB_FILE) as database:
        ensure_db(database)

        actions[action](database, arguments)


if __name__ == '__main__':
    main(sys.argv[1:])

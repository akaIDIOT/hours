#!/usr/bin/env python3

from datetime import date, timedelta
from os import path
import re
import sqlite3
import sys

from tabulate import tabulate


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
            CREATE TABLE IF NOT EXISTS aliases (
                alias TEXT PRIMARY KEY,
                name TEXT
            )
        """
    )
    database.execute(
        """
            CREATE INDEX IF NOT EXISTS days ON hours ( day )
        """
    )


def select_day(argument):
    if argument in DAYS:
        return DAYS[argument]

    if DATE_PATTERN.match(argument):
        year, month, day = argument.split('-')
        return date(int(year), int(month), int(day))

    raise ValueError('not a day: {}'.format(argument))


def to_name(database, argument):
    cursor = database.execute(
        """
            SELECT name FROM aliases WHERE alias = ?
        """,
        (argument,)
    )
    name = cursor.fetchone()
    if name:
        return name[0]
    else:
        return argument


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
        if argument in DAYS or DATE_PATTERN.match(argument):
            day = select_day(argument)
        elif HOURS_PATTERN.match(argument):
            hours = float(argument.replace(',', '.'))
        else:
            name = to_name(database, argument)

    assert None not in (name, day, hours)

    return log_hours(database, name, day, hours)


def show_day(database, day):
    cursor = database.execute(
        """
            SELECT name, SUM(hours) FROM hours WHERE day = ? GROUP BY name ORDER BY name
        """,
        (day,)
    )

    print(tabulate(cursor.fetchall(),
                   headers=('', day.isoformat())))


def show_range(database, start, end):
    days = [(start + timedelta(days=offset)).isoformat() for offset in range((end - start).days + 1)]

    cursor = database.execute(
        """
            SELECT name, day, SUM(hours) FROM hours WHERE day >= ? AND day <= ? GROUP BY name, day ORDER BY name, day
        """,
        (start, end)
    )

    data = {(name, day): hours for (name, day, hours) in cursor.fetchall()}
    names = sorted({name for (name, day) in data.keys()})

    print(tabulate([[name] + [data.get((name, day)) for day in days] for name in names],
                   headers=[''] + days))


def do_show(database, arguments):
    assert 0 <= len(arguments) <= 2

    if len(arguments) == 2:
        start = select_day(arguments[0])
        end = select_day(arguments[1])
    elif len(arguments) == 1 and arguments[0] != 'week':
        start = end = select_day(arguments[0])
    else:
        start = WEEK_START
        end = WEEK_START + timedelta(days=6)

    if start == end:
        return show_day(database, start)
    else:
        return show_range(database, *sorted((start, end)))


def create_alias(database, arguments):
    assert len(arguments) == 2

    database.execute(
        """
            INSERT OR REPLACE INTO aliases (alias, name) VALUES (?, ?)
        """,
        arguments
    )


def main(arguments):
    actions = {
        'log': do_log,
        'show': do_show,
        'alias': create_alias,
    }

    action = 'log'
    if arguments[0] in actions:
        action = arguments.pop(0)

    with sqlite3.connect(DB_FILE) as database:
        ensure_db(database)

        actions[action](database, arguments)


if __name__ == '__main__':
    main(sys.argv[1:])

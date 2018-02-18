#!/usr/bin/env python3

from datetime import date, timedelta
from os import path
import re
import sqlite3
import sys

from tabulate import tabulate


DATE_PATTERN = re.compile(r'^\d\d\d\d-\d\d-\d\d$')


HOURS_PATTERN = re.compile(r'^(\d+[,.])?\d+$')


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


class Session:
    def __init__(self, db_path, today=None):
        self.db_path = db_path
        self._database = None
        self.today = today or date.today()

        self.week_start = self.today - timedelta(days=self.today.weekday())        
        self.days = {day: self.week_start + timedelta(days=week_index) for week_index, day in enumerate(('monday',
                                                                                                         'tuesday',
                                                                                                         'wednesday',
                                                                                                         'thursday',
                                                                                                         'friday',
                                                                                                         'saturday',
                                                                                                         'sunday'))}
        self.days.update(today=self.today,
                         yesterday=self.today - timedelta(days=1),
                         tomorrow=self.today + timedelta(days=1))

    @property
    def database(self):
        if not self._database:
            self._database = sqlite3.connect(self.db_path)

        return self._database

    def select_day(self, argument):
        if argument in self.days:
            return self.days[argument]

        if DATE_PATTERN.match(argument):
            year, month, day = argument.split('-')
            return date(int(year), int(month), int(day))

        raise ValueError('not a day: {}'.format(argument))

    def to_name(self, argument):
        cursor = self.database.execute(
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

    def log_hours(self, name, day, hours):
        self.database.execute(
            """
                INSERT INTO hours (name, day, hours) VALUES (?, ?, ?)
            """,
            (name, day, hours)
        )

    def run_log(self, arguments):
        assert 2 <= len(arguments) <= 3

        day = self.today
        name = hours = None

        for argument in arguments:
            if argument in self.days or DATE_PATTERN.match(argument):
                day = self.select_day(argument)
            elif HOURS_PATTERN.match(argument):
                hours = float(argument.replace(',', '.'))
            else:
                name = self.to_name(argument)

        assert None not in (name, day, hours)

        return self.log_hours(name, day, hours)

    def show_day(self, day):
        cursor = self.database.execute(
            """
                SELECT name, SUM(hours) FROM hours WHERE day = ? GROUP BY name ORDER BY name
            """,
            (day,)
        )

        print(tabulate(cursor.fetchall(),
                       headers=('', day.isoformat())))

    def show_range(self, start, end):
        days = [(start + timedelta(days=offset)).isoformat() for offset in range((end - start).days + 1)]

        cursor = self.database.execute(
            """
                SELECT name, day, SUM(hours) FROM hours WHERE day >= ? AND day <= ? GROUP BY name, day ORDER BY name, day
            """,
            (start, end)
        )

        data = {(name, day): hours for (name, day, hours) in cursor.fetchall()}
        names = sorted({name for (name, day) in data.keys()})

        print(tabulate([[name] + [data.get((name, day)) for day in days] for name in names],
                       headers=[''] + days))

    def run_show(self, arguments):
        assert 0 <= len(arguments) <= 2

        if len(arguments) == 2:
            if arguments == ['last', 'week']:
                start = self.week_start - timedelta(days=7)
                end = self.week_start - timedelta(days=1)
            else:
                start = self.select_day(arguments[0])
                end = self.select_day(arguments[1])
        elif len(arguments) == 1 and arguments[0] != 'week':
            start = end = self.select_day(arguments[0])
        else:
            start = self.week_start
            end = self.week_start + timedelta(days=6)

        if start == end:
            return self.show_day(start)
        else:
            return self.show_range(*sorted((start, end)))

    def create_alias(self, arguments):
        assert len(arguments) == 2

        self.database.execute(
            """
                INSERT OR REPLACE INTO aliases (alias, name) VALUES (?, ?)
            """,
            arguments
        )

    def run(self, arguments):
        actions = {
            'log': self.run_log,
            'show': self.run_show,
            'alias': self.create_alias,
        }

        action = 'log'
        if arguments[0] in actions:
            action = arguments.pop(0)

        with self.database:
            ensure_db(self.database)

            actions[action](arguments)


if __name__ == '__main__':
    Session(DB_FILE).run(sys.argv[1:])

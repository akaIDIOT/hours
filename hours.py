#!/usr/bin/env python3

import sys


def log_hours(name, date, hours):
    pass


def show_day(date):
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

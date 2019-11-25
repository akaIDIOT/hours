hours
=====

*Stupid script to track stupid hours…*

Usage
-----

`hours` uses a sequence of positional arguments to figure out what to do, something like the following:

~~~~
$ hours log 2 today project-a
~~~~

Command above will log 2 hours on "project-a" for today. 
Some of these values are the default, so the following would result in the same:

~~~~
$ hours project-a 2
~~~~

Confusing, no?
`hours` distinguishes 3 main commands:

- `log` (the default): log hours;
- `show`: print a table for a particular timespan, the current week by default;
- `alias`: create a handy alias.

All of this allows an interaction as such:

~~~~
$ hours alias project-a "1234AB: That project with the complicated code"
$ hours log 2 project-a
$ hours show
~~~~

Magic values
------------

Purely by example:

- `hours show`
- `hours show week`
- `hours show last week`
- `hours log 2 today project`
- `hours log 2 yesterday project`
- `hours log 2 tomorrow project` (**manager:** *what the hell are you up to…?*)

Configuration
-------------

`hours` uses `confidence` for configuration, currently reading just one key: `database.path`, defaulting to `~/.hours.db`.

Errors
------

Both `hours` and the developer are lazy, errors are generally just `AssertionError`s when there's stuff missing.
Should the database schema change over time, expect SQLITE-related errors ;).

eusay
=====
eusay is a voting and discussion platform where students can submit proposals to the student union and vote/comment on each other's ideas. Students get a platform, and the student union gets information on what the students want. Everyone wins.

eusay was born during the Smart Data Hack in the 2014 Innovative Learning Week at the University of Edinburgh. It was picked up by the student union, EUSA, and can be seen [here](http://eusay.eusa.ed.ac.uk).

eusay is funded by the [Jisc Summer of Student Innovation](http://elevator.jisc.ac.uk/sosi14/) competition.

Requirements
------------
eusay runs on Django 1.7 on Python 3. The database is PostgreSQL. See requirements.txt for package requirements.

Setup
-----
Run `python manage.py syncdb` to create the database. Optionally, load demo tags with `python manage.py loaddata tags`. Start a local development server with `python manage.py runserver`.

The cron jobs in the crontab file updates proposal ranks every 15 minutes, and sends out notification emails daily to those are subscribed.

To Do:
------
* See [Trello](https://trello.com/b/yVdFBRrd/eusay) and [GitHub issue tracker](https://github.com/HughMcGrade/eusay/issues)

Known issues:
-------------
* See [issue tracker](https://github.com/HughMcGrade/eusay/issues) on GitHub
* `python manage.py rebuild_index` deletes the search index, which means that its permissions are lost. This means that the server cannot update the search index. Make sure to set permissions on `core/settings/whoosh_index` after running this command.
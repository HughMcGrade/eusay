eusay
=====
eusay is a voting and discussion platform where students can submit proposals to the student union and vote/comment on each other's ideas. Students get a platform, and the student union gets information on what the students want. Everyone wins.

eusay was born during the Smart Data Hack in the 2014 Innovative Learning Week at the University of Edinburgh.

eusay is funded by the [Jisc Summer of Student Innovation](http://elevator.jisc.ac.uk/sosi14/) competition.

Requirements
------------
eusay runs on Django on Python 3. The database is PostgreSQL. It uses Redis to store its task queue.

See requirements.txt for package requirements.

Setup
-----
Run `python manage.py syncdb` to create the database. Optionally, load demo tags with `python manage.py loaddata tags`. Start a local development server with `python manage.py runserver --settings=eusay.settings.dev`.

Start the task queue with `celery -A eusay worker -B`. This will eventually run as a daemon, WIP.


To Do:
------
* See [Trello](https://trello.com/b/yVdFBRrd/eusay)
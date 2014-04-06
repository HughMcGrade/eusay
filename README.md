eusay
=====
eusay is a place where students can submit policy proposals and vote/comment on each other's ideas. Students get a platform, and EUSA gets information on what the students want. Everyone wins.

eusay was born during the Smart Data Hack in the 2014 Innovative Learning Week at the University of Edinburgh.


Requirements
------------
eusay runs on Django on Python 3. The database is SQLite, but will probably be PostgreSQL soon.
Our test server runs Apache 2.2.15.
See requirements.txt.

Setup
-----
Navigate to the main eusay directory and run `python manage.py syncdb` to create the database.  
If you want some example data, run `python manage.py loaddata exampledata`.  
Set up a local server with `python manage.py runserver`.


To Do:
------
* Make settings.py syncable with git without breaking anything
* Markdown comments would be cool ([1][django_markdown])
* Include proposer on proposals page/list
* Add features for representatives and candidates
* Right now the front page loads every proposal there is. Set up a page system or a nice AJAX load-on-scroll thing.
* Set up EASE authentication ([1][ease1]) ([2][ease2]) ([This has to wait](#footnote1))


Questions
------------
* What information does EASE give about a user? If no name, how should we identify users on the site?
* Should anonymous proposals be accepted?


Footnotes
---------
<a name="footnote1"></a>
We need to talk to the university and:  
1) Register for an Ed Uni signed certificate for the web server <-> cosign server back-channel. You can also use this as your front-facing SSL cert if they want to keep things simple.  
2) Register your Web service with Cosign. We would need to know:  
a) The FQDN of the Web Service Host being registered.  
b) The CN of the certificate being used (usually the same as a) )  
c) If you are using HTTP or HTTPS for your web service (we recommend HTTPS but it's not essential).  
Because of this, EASE can't be set up until we know the domain that eusay will reside on.

[ease1]: https://www.wiki.ed.ac.uk/display/AuthService/Central+Authorisation+Service+-+Home
[ease2]: https://www.ease.ed.ac.uk/admindocs/
[django_markdown]: https://github.com/klen/django_markdown

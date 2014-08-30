from django.db import models


class StudentCouncil(models.Model):
    datetime = models.DateTimeField()

    def __unicode__(self):
        return self.datetime.strftime("%a %d %b, %I:%M %p")
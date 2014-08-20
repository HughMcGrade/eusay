from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from votes.models import Vote

class Content(models.Model):
    id = models.AutoField(primary_key=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    lastModified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    upVotes = models.IntegerField(default=0)
    downVotes = models.IntegerField(default=0)
    isHidden = models.BooleanField(default=False)

    def get_votes_count(self, isUp):
        try:
            return len(Vote.get_votes(self).filter(isVoteUp=isUp))
        except Exception:
            return 0

    def get_votes_up_count(self):
        #return self.get_votes_count(True)
        return self.upVotes

    def get_votes_down_count(self):
        #return self.get_votes_count(False)
        return self.downVotes

    def get_votes(self):
        return self.votes

    def get_voters(self, target="all"):
        content_type = ContentType.objects.get_for_model(self)
        users = get_user_model().objects.\
            filter(votes__content_type=content_type).\
            filter(votes__object_id=self.id)
        if target == "all":
            return users
        elif target == "for":
            return users.filter(votes__isVoteUp=True)
        elif target == "against":
            return users.filter(votes__isVoteUp=False)

    class Meta:
        abstract = True
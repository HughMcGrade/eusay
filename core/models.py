"""Core models module defining abstract model Content"""

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

class Content(models.Model):
    """
    Abstract model for website content.

    Content models should be subclassed to create models for user content such
    as proposals and comments which can be voted on, ranked and moderated.

    :ivar id:            Primary key for content subclasses
    :ivar createdAt:     DateTime of creation
    :ivar lastModified:  DateTime of last modification
    :ivar user:          Creator of content
    :ivar upVotes:       Up vote count, set by save method of Vote model(only!)
    :ivar downVotes:     Down vote count, set by :meth:``votes.Vote.save``(only!)
    :ivar isHidden:      True if the content has been hidden, set by save\
                         method of HideAction (only!)
    :ivar rank:          Rank of the content for ordering by popularity, set by\
                         cron job

    """
    id = models.AutoField(primary_key=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    lastModified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    upVotes = models.IntegerField(default=0)
    downVotes = models.IntegerField(default=0)
    isHidden = models.BooleanField(default=False)
    rank = models.FloatField(default=0.0)

    def get_votes_count(self, isUp):
        """
        Query vote table and return number of either up or down votes.

        :rtype: integer
        """
        return self.votes.filter(isVoteUp=isUp).count()

    def get_voters(self, target="all"):
        """
        Get users who have voted on this content.

        :param target: ``"all"`` (default) for all users, ``"up"`` for voters for and ``"down"`` for voters against
        :rtype: QuerySet
        """
        content_type = ContentType.objects.get_for_model(self)
        users = get_user_model().objects\
                                .filter(votes__content_type=content_type)\
                                .filter(votes__object_id=self.id)
        if target == "all":
            return users
        elif target == "up":
            return users.filter(votes__isVoteUp=True)
        elif target == "down":
            return users.filter(votes__isVoteUp=False)

    class Meta:
        abstract = True

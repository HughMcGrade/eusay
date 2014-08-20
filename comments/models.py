import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType

from core.models import Content

class CommentManager(models.Manager):

    def get_visible_comments(self, proposal, reply_to=None, sort="popularity"):
        comments = self.filter(proposal=proposal).filter(replyTo=reply_to)\
                                                 .filter(isHidden=False)\
                                                 .select_related('user')
        if sort == "popularity":
            return sorted(comments, key=lambda c: c.get_score(), reverse=True)
        elif sort == "newest":
            return sorted(comments, key=lambda c: c.createdAt)


class Comment(Content):
    # The maximum length of 'text' is 6100 because a proposal can have 6000
    # characters in its body and 100 in its title. Because amendments are
    # stored as Comments, they must be at least as long as Proposals.
    text = models.CharField(max_length=6100)
    proposal = models.ForeignKey('proposals.Proposal', null=False,\
                                 related_name="comments")
    replyTo = models.ForeignKey("self", null=True)
    isAmendment = models.BooleanField(default=False)

    objects = CommentManager()

    def contentType():
        return ContentType.objects.get(app_label="comments", model="comment")

    def is_new(self):
        """
        :return: True if the comment is less than 5 minutes old
        """
        timesince = datetime.datetime.now() - self.createdAt
        return timesince < datetime.timedelta(minutes=5)

    def get_replies(self, sort="popularity"):
        if sort == "popularity":
            return sorted([c for c in Comment.objects.filter(replyTo=self)\
                           .select_related('user')], key=lambda c: c.get_score)
        elif sort == "chronological":
            return [c for c in Comment.objects.filter(replyTo=self)\
                    .select_related('user').order_by("createdAt")]

    def get_score(self):
        return self.get_votes_up_count() - self.get_votes_down_count()

    def __unicode__(self):
        return "%s" % self.text

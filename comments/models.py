import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType

from core.models import Content
from votes.models import Vote

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

    def get_content_type():
        if not hasattr(Comment, '_content_type'):
            Comment._content_type = ContentType.objects.get(app_label="comments", model="comment")
        return Comment._content_type

    def save(self, *args, **kwargs):
        is_initial = not self.pk
        super(Comment, self).save(*args, **kwargs)
        # when the comment is first created, add a vote by the commenter
        if is_initial:
            Vote.objects.create(user=self.user, content=self, isVoteUp=True)


    def is_new(self):
        """
        :return: True if the comment is less than 5 minutes old
        """
        timesince = datetime.datetime.now() - self.createdAt
        return timesince < datetime.timedelta(minutes=5)

    def get_replies(self, sort="popularity"):
        if sort == "popularity":
            return Comment.objects.filter(replyTo=self)\
                .select_related('user').order_by("rank")
        elif sort == "chronological":
            return Comment.objects.filter(replyTo=self)\
                .select_related('user').order_by("createdAt")

    def get_score(self):
        return self.upVotes - self.downVotes

    def __unicode__(self):
        return "%s" % self.text

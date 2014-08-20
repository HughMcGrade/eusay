from django.db import models
from django.core.urlresolvers import reverse
import datetime
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect

from core.utils import better_slugify
from core.models import Content
from tags.models import Tag
from votes.models import Vote
from comments.models import Comment

class ProposalManager(models.Manager):

    def get_visible_proposals(self, tag=None, sort="popular"):
        proposals = self.all()
        if tag:
            proposals = proposals.filter(tags=tag)

        if sort == "popular":
            proposals = proposals.order_by("-rank")
        elif sort == "newest":
            proposals = proposals.order_by("-createdAt")

        return proposals.filter(isHidden=False)


class Proposal(Content):
    title = models.CharField(max_length=100)
    text = models.TextField()
    slug = models.SlugField(default="slug", max_length=100)
    tags = models.ManyToManyField(Tag, related_name="proposals")
    rank = models.FloatField(default=0.0)

    objects = ProposalManager()

    def contentType():
        return ContentType.objects.get(app_label="proposals", model="proposal")

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_initial = not self.pk
        self.slug = better_slugify(self.title)
        super(Proposal, self).save(*args, **kwargs)
        # when the proposal is first created, add a vote by the proposer
        if is_initial:
            Vote.objects.create(user=self.user, content=self, isVoteUp=True)

    def get_absolute_url(self):
        return reverse("proposal", kwargs={"proposalId": self.id,
                                           "slug": self.slug})

    def get_votes_up_percentage(self):
        votes_up = self.get_votes_up_count()
        votes_total = votes_up + self.get_votes_down_count()
        if votes_total == 0:
            return 0
        else:
            return (votes_up/votes_total) * 100

    def get_votes_down_percentage(self):
        votes_up_percentage = self.get_votes_up_percentage()
        return 100 - votes_up_percentage

    def _hours_since(self, date):
        utc_now = datetime.datetime.utcnow()
        utc_event = datetime.datetime.utcfromtimestamp(date.timestamp())
        return (utc_now - utc_event).total_seconds() / 3600.0

    def _weight_instance(self, hour_age, gravity=1.8):
        return 1 / pow((hour_age+2), gravity)

    def _proximity_coefficient(self):
        return 1

    def get_rank(self):
        rank = 0

        # Take sum of weighted value for each comment
        comments = Comment.objects.all().filter(proposal=self)
        for comment in comments:
            rank += self._weight_instance(hour_age=
                                          self._hours_since(
                                              comment.createdAt)) * 4

        votes = user.get_votes()#Vote.get_votes(self)
        for vote in votes:
            hour_age = self._hours_since(vote.createdAt)
            if vote.isVoteUp:
                rank += self._weight_instance(hour_age) * 2
            else:
                rank += self._weight_instance(hour_age) * 1

        return rank * \
            self._proximity_coefficient() + \
            self.get_votes_up_count() - \
            self.get_votes_down_count()

    def get_visible_comments(self, reply_to=None, sort="popularity"):
        return Comment.objects.get_visible_comments\
            (proposal=self, reply_to=reply_to, sort=sort)

class Response(Content):
    text = models.TextField()
    proposal = models.OneToOneField(Proposal, related_name="response")

    def save(self, *args, **kwargs):
        if self.user.userStatus == "Staff" or \
           self.user.userStatus == "Officeholder":
            super(Response, self).save(*args, **kwargs)
        else:
            raise Exception\
                ("Only staff and officerholders can respond to proposals!")
            def __unicode__(self):
                return "%s" % self.text

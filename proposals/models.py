
from django.db import models
from django.core.urlresolvers import reverse
import datetime
from slugify import slugify
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect

from core.models import Content
from tags.models import Tag
from votes.models import Vote
from comments.models import Comment
from student_councils.models import StudentCouncil


class ProposalManager(models.Manager):
    """Manager for Proposal model"""
    def get_visible_proposals(self, tag=None, sort="popular"):
        """
        Get visible proposals, optionally for a particular tag.

        By default, proposals are sorted most popular first. To sort newest
        proposal first, pass ``"newest"`` as the ``sort`` argument.

        :param tag:  Tag to get proposals for (None by default)
        :param sort: Sort by either popularity (``"popular"``) or ``createdAt``
        (``"newest"``)
        :returns:    Sorted and filtered proposals with hidden proposals
                     removed
        :rtype:      QuerySet
        """
        proposals = self.all()
        if tag:
            proposals = proposals.filter(tags=tag)

        if sort == "popular":
            proposals = proposals.order_by("-rank")
        elif sort == "newest":
            proposals = proposals.order_by("-createdAt")

        return proposals.filter(isHidden=False)


class Proposal(Content):
    PROPOSAL_STATUS_CHOICES = (
        (1, "Open for discussion"),
        (2, "Work in progress"),
        (3, "Going to Student Council"),
        (4, "Resolved")
    )
    title = models.CharField(max_length=100)
    text = models.TextField()
    slug = models.SlugField(default="slug", max_length=100)
    tags = models.ManyToManyField(Tag, related_name="proposals")
    status = models.IntegerField(choices=PROPOSAL_STATUS_CHOICES, default=1)
    student_council = models.ForeignKey(StudentCouncil,
                                        related_name="proposals",
                                        null=True)

    objects = ProposalManager()

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def get_content_type():
        """
        Gets ContentType of Proposal model, caching result in ``_content_type``
        when first retrieved.

        :returns: ContentType of Proposal model
        :rtype:   :mod:`django.contrib.contenttypes.models.ContentType`
        """
        if not hasattr(Proposal, '_content_type'):
            Proposal._content_type = ContentType.objects.get(
                app_label="proposals", model="proposal")
        return Proposal._content_type

    def save(self, *args, **kwargs):
        """
        Create slug, save proposal and for initial save add
        vote by proposer.
        """
        is_initial = not self.pk
        self.slug = slugify(self.title, max_length=100)
        super(Proposal, self).save(*args, **kwargs)
        # when the proposal is first created, add a vote by the proposer
        if is_initial:
            Vote.objects.create(user=self.user, content=self, isVoteUp=True)

    def get_absolute_url(self):
        """
        Get the proposal's URL using :mod:`django.core.urlresolvers.reverse`
        """
        return reverse("proposal", kwargs={"proposal_id": self.id,
                                           "slug": self.slug})

    def get_votes_up_percentage(self):
        """
        Get percentage of votes which are up votes
        """
        votes_up = self.upVotes
        votes_total = votes_up + self.downVotes
        if votes_total == 0:
            return 0
        else:
            return (votes_up/votes_total) * 100

    def get_votes_down_percentage(self):
        """
        Get percentage of votes which are down votes
        """
        votes_up_percentage = self.get_votes_up_percentage()
        return 100 - votes_up_percentage

    @staticmethod
    def _hours_since(date):
        utc_now = datetime.datetime.utcnow()
        utc_event = datetime.datetime.utcfromtimestamp(date.timestamp())
        return (utc_now - utc_event).total_seconds() / 3600.0

    @staticmethod
    def _weight_instance(hour_age, gravity=1.8):
        return 1 / pow((hour_age+2), gravity)

    @staticmethod
    def _proximity_coefficient():
        return 1

    def get_rank(self):
        rank = 0

        # Take sum of weighted value for each comment
        comments = Comment.objects.filter(proposal=self)
        for comment in comments:
            rank += Proposal._weight_instance(
                    hour_age=Proposal._hours_since(comment.createdAt)) * 4

        votes = self.user.get_votes()
        # Vote.get_votes(self)
        for vote in votes:
            hour_age = Proposal._hours_since(vote.createdAt)
            if vote.isVoteUp:
                rank += Proposal._weight_instance(hour_age) * 2
            else:
                rank += Proposal._weight_instance(hour_age) * 1

        return rank * \
            Proposal._proximity_coefficient() + \
            self.upVotes - \
            self.downVotes

    def get_visible_comments(self, reply_to=None, sort="popularity"):
        return Comment.objects.get_visible_comments(
            proposal=self, reply_to=reply_to, sort=sort)


class Response(Content):
    text = models.TextField()
    proposal = models.ForeignKey(Proposal, related_name="responses")

    def save(self, *args, **kwargs):
        if self.user.userStatus == "Staff" or \
           self.user.userStatus == "Officeholder":
            super(Response, self).save(*args, **kwargs)
        else:
            raise Exception("Only staff and officerholders "
                            "can respond to proposals!")

    def __unicode__(self):
        return "%s" % self.text

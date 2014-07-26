'''
Created on 18 Feb 2014

@author: Hugh
'''
from django.db import models
from django.core.urlresolvers import reverse
import datetime

from .utils import better_slugify

class Comment (models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=500) # TODO: is this a good length? implement client-side character count
    createdAt = models.DateTimeField(auto_now_add=True)
    lastModified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey("User", related_name="comments")
    proposal = models.ForeignKey("Proposal", null=False, related_name="comments")
    replyTo = models.ForeignKey("self", null=True)
    
    def _get_votes_count(self, isUp):
        try:
            return len(CommentVote.objects.all().filter(comment=self).filter(isVoteUp=isUp))
        except Exception:
            return 0

    def get_votes_up_count(self):
        return self._get_votes_count(True)
        
    def get_votes_down_count(self):
        return self._get_votes_count(False)

    def get_replies(self):
        return Comment.objects.filter(replyTo = self)

    def get_score(self):
        return self.get_votes_up_count() - self.get_votes_down_count()

    def is_hidden(self):
        return HideCommentAction.objects.all().filter(comment=self).exists()

    def __unicode__(self):
        return "%s" % self.text

    def get_visible_comments(self, proposal, reply_to=None):
        return [c for c in Comment.objects.all().filter(proposal = proposal).filter(replyTo = reply_to) if not c.is_hidden()]

class Vote (models.Model):
    id = models.AutoField(primary_key=True)
    isVoteUp = models.BooleanField()
    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("User")

    class Meta:
        abstract = True

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(default="slug")
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.slug = better_slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tag", kwargs={"tagId": self.id, "slug": self.slug})

    def __unicode__(self):
        return self.name


class Proposal (models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    text = models.TextField()
    slug = models.SlugField(default="slug")
    proposer = models.ForeignKey("User", related_name="proposed")
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    lastModified = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name="proposals")

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = better_slugify(self.title)
        super(Proposal, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("proposal", kwargs={"proposalId": self.id,
                                           "slug": self.slug})

    def _get_votes_count(self, isUp):
        try:
            return len(ProposalVote.objects.all().filter(proposal=self).filter(isVoteUp = isUp))
        except Exception:
            return 0
    
    def get_votes_up_count(self):
        return self._get_votes_count(True)
    
    def get_votes_down_count(self):
        return self._get_votes_count(False)

    def get_votes_up_percentage(self):
        votes_up = self.get_votes_up_count()
        votes_total = votes_up + self.get_votes_down_count()
        if votes_total == 0:
            return 0;
        else:
            return (votes_up/votes_total) * 100

    def get_votes_down_percentage(self):
        votes_up_percentage = self.get_votes_up_percentage()
        if votes_up_percentage == 0:
            return 0
        else:
            return 100 - votes_up_percentage
    
    def _hours_since(self, date):
        utc_now = datetime.datetime.utcnow()#(datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(timestamp))
        utc_event = datetime.datetime.utcfromtimestamp(date.timestamp())
        return (utc_now - utc_event).total_seconds() / 3600.0
    
    def _weight_instance(self, hour_age, gravity=1.8):
        return 1 / pow((hour_age+2), gravity)
    
    def _proximity_coefficient(self):
        return 1
    
    def get_score(self):
        
        score = 0
        
        # Take sum of weighted value for each comment
        comments = Comment.objects.all().filter(proposal=self)
        for comment in comments:
            score += self._weight_instance(hour_age = self._hours_since(comment.createdAt)) * 4
        
        votes = ProposalVote.objects.all().filter(proposal=self)
        for vote in votes:
            hour_age = self._hours_since(vote.createdAt)
            if vote.isVoteUp:
                score += self._weight_instance(hour_age) * 2
            else:
                score += self._weight_instance(hour_age) * 1
        
        return score * self._proximity_coefficient() + self.get_votes_up_count() - self.get_votes_down_count()

    def is_hidden(self):
        return HideProposalAction.objects.all().filter(proposal=self).exists()

    def get_visible_comments(self, reply_to=None):
        return [c for c in self.comments.filter(replyTo = reply_to) if not c.is_hidden()]

    @staticmethod
    def get_visible_proposals(tag=None):
        if tag:
            return sorted([p for p in tag.proposals.all() if not p.is_hidden()], key = lambda p: p.get_score())
        else:
            return sorted([p for p in Proposal.objects.all() if not p.is_hidden()], key = lambda p: p.get_score())

class ProposalVote (Vote):
    proposal = models.ForeignKey(Proposal, related_name="votes")
    
class CommentVote (Vote):
    comment = models.ForeignKey(Comment, related_name="votes")
    
class User (models.Model):
    # The first element in each tuple is the actual value to be stored,
    # and the second element is the human-readable name.
    USER_STATUS_CHOICES = (
        ("User", "Regular User"),
        ("Staff", "EUSA Staff"),
        ("Candidate", "EUSA Candidate"),
        ("Officeholder", "EUSA Officeholder")
    )
    sid = models.CharField("student ID", max_length=20, primary_key=True)
    name = models.CharField(max_length=50, unique=True, null=False)
    slug = models.SlugField(default="slug")
    createdAt = models.DateTimeField("date created",
                                     default=datetime.datetime.now,
                                     editable=False)
    userStatus = models.CharField("user status",
                                  max_length=12,
                                  choices=USER_STATUS_CHOICES,
                                  default="User")
    title = models.CharField(max_length=100)
    isModerator = models.BooleanField("moderator", default=False)
    hasProfile = models.BooleanField("public profile", default=False)

    def save(self, *args, **kwargs):
        self.slug = better_slugify(self.name, domain="User")
        super(User, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("user", kwargs={"slug": self.slug})

    def get_proposals_voted_for(self):
        """
        Returns a QuerySet of proposals that the user has voted for.
        """
        user_votes = ProposalVote.objects.filter(user=self).filter(isVoteUp=True)
        return Proposal.objects.filter(votes__in=user_votes)

    def get_proposals_voted_against(self):
        """
        Returns a QuerySet of proposals that the user has voted against.
        """
        user_votes = ProposalVote.objects.filter(user=self).filter(isVoteUp=False)
        return Proposal.objects.filter(votes__in=user_votes)

    def __unicode__(self):
        return self.name + " (" + self.sid + ")"

class HideAction (models.Model):
    id = models.AutoField(primary_key=True)
    moderator = models.ForeignKey(User)
    createdAt = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=2000)

    def save(self, *args, **kwargs):
        if not self.moderator.isModerator:
            raise Exception("Only moderators may perform hide actions!")
        else:
            super(HideAction, self).save()

class HideCommentAction (HideAction):
    comment = models.ForeignKey(Comment, related_name="hideActions")

class HideProposalAction (HideAction):
    proposal = models.ForeignKey(Proposal, related_name="hideActions")

class Report (models.Model):
    id = models.AutoField(primary_key=True)
    reporter = models.ForeignKey(User)
    createdAt = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=2000)

class CommentReport (Report):
    comment = models.ForeignKey(Comment, related_name="reports")

class ProposalReport (Report):
    proposal = models.ForeignKey(Proposal, related_name="reports")

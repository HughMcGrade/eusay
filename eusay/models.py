'''
Created on 18 Feb 2014

@author: Hugh
'''
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
import datetime
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import models as usermodels


from .utils import better_slugify


class Content (models.Model):
    id = models.AutoField(primary_key=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    lastModified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey("User")
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

    def is_hidden(self):
        return self.isHidden
        #content_type = ContentType.objects.get_for_model(self)
        #return HideAction.get_hide_actions(object_id=self.id, content_type=content_type).exists()
        #return HideAction.objects.all().filter(content=self).exists()

    class Meta:
        abstract = True

class Comment (Content):
    text = models.CharField(max_length=1000)
    proposal = models.ForeignKey("Proposal", null=False, related_name="comments")
    replyTo = models.ForeignKey("self", null=True)
    ##contentType = ContentType.objects.get(app_label="eusay", model="comment")
    
    def contentType():
        return ContentType.objects.get(app_label="eusay", model="proposal")

    def get_replies(self, sort="popularity"):
        if sort == "popularity":
            return sorted([c for c in Comment.objects.filter(replyTo=self).select_related('user')],
                          key=lambda c: c.get_score)
        elif sort == "chronological":
            return [c for c in
                    Comment.objects.filter(replyTo=self).select_related('user').order_by("createdAt")]

    def get_score(self):
        return self.get_votes_up_count() - self.get_votes_down_count()

    def __unicode__(self):
        return "%s" % self.text

    def get_visible_comments(self, proposal, reply_to=None):
        return [c for c in Comment.objects.all().filter(content = proposal).filter(replyTo = reply_to) if not c.is_hidden()]

class Vote (models.Model):
    isVoteUp = models.BooleanField()
    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("User")

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey()

    @staticmethod
    def get_votes(content):
        content_type = ContentType.objects.get_for_model(content)
        return Vote.objects.filter(content_type=content_type, object_id=content.id)

    def save(self, *args, **kwargs):
        super(Vote, self).save(*args, **kwargs)
        self.content.upVotes = self.content.get_votes_count(True)
        self.content.downVotes = self.content.get_votes_count(False)
        self.content.save()

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(default="slug", max_length=100)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.slug = better_slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tag", kwargs={"tagId": self.id, "slug": self.slug})

    def __unicode__(self):
        return self.name

class Proposal (Content):
    title = models.CharField(max_length=100)
    text = models.TextField()
    slug = models.SlugField(default="slug", max_length=100)
    tags = models.ManyToManyField(Tag, related_name="proposals")
    rank = models.FloatField(default=0.0)
    #contentType = ContentType.objects.get(app_label="eusay", model="proposal")

    def contentType():
        return ContentType.objects.get(app_label="eusay", model="proposal")

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
            return 0;
        else:
            return (votes_up/votes_total) * 100

    def get_votes_down_percentage(self):
        votes_up_percentage = self.get_votes_up_percentage()
        return 100 - votes_up_percentage
    
    def _hours_since(self, date):
        utc_now = datetime.datetime.utcnow()#(datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(timestamp))
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
        
        votes = Vote.get_votes(self)
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
        if sort == "popularity":
            return sorted([c for c in self.comments.filter(replyTo=reply_to).select_related('user')
                           if not c.is_hidden()],
                          key=lambda c: c.get_score(),
                          reverse=True)
        elif sort == "newest":
            return sorted([c for c in self.comments.filter(replyTo=reply_to).select_related('user')
                           if not c.is_hidden()],
                          key=lambda c: c.createdAt)


    @staticmethod
    def get_visible_proposals(tag=None, sort="popular"):
        proposals = Proposal.objects.all()
        if tag:
            proposals = proposals.filter(tags=tag)

        if sort == "popular":
            proposals = proposals.order_by("-rank")
        elif sort == "newest":
            proposals = proposals.order_by("-createdAt")

        return [p for p in proposals if not p.is_hidden()]


class Response(Content):
    text = models.TextField()
    proposal = models.OneToOneField(Proposal, related_name="response")

    def save(self, *args, **kwargs):
        if self.user.userStatus == "Staff" or \
           self.user.userStatus == "Officeholder":
            super(Response, self).save(*args, **kwargs)
        else:
            raise Exception("Only staff and officerholders can respond to proposals!")

    def __unicode__(self):
        return "%s" % self.text


class User(usermodels.AbstractUser):
    # The first element in each tuple is the actual value to be stored,
    # and the second element is the human-readable name.
    USER_STATUS_CHOICES = (
        ("User", "Regular User"),
        ("Staff", "EUSA Staff"),
        ("Candidate", "EUSA Candidate"),
        ("Officeholder", "EUSA Officeholder")
    )
    sid = models.CharField("student ID", max_length=20, unique=True)
    slug = models.SlugField(default="slug")
    userStatus = models.CharField("user status",
                                  max_length=12,
                                  choices=USER_STATUS_CHOICES,
                                  default="User")
    title = models.CharField(max_length=100, blank=True)
    isModerator = models.BooleanField("moderator", default=False)
    hasProfile = models.BooleanField("public profile", default=False)

    # Use UserManager to get the create_user method, etc.
    objects = usermodels.UserManager()

    def proposed(self):
        return Proposal.objects.all().filter(user=self)

    def comments(self):
        return Comment.objects.all().filter(user=self)

    def save(self, *args, **kwargs):
        self.slug = better_slugify(self.username, domain="User")
        super(User, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("user", kwargs={"slug": self.slug})

    def get_vote_on(self, content):
        content_type = ContentType.objects.get_for_model(content)
        try:
            vote = Vote.objects.get(user=self, content_type=content_type, object_id=content.id)
            if vote.isVoteUp:
                return 1
            else:
                return -1
        except Vote.DoesNotExist:
            return 0

    def get_proposals_voted_for(self):
        """
        Returns a list (formerly QuerySet) of proposals that the user has voted for.
        """
        user_votes = Vote.objects.filter(user=self).filter(content_type=Proposal.contentType()).filter(isVoteUp=True)
        return [vote.content for vote in user_votes]

    def get_proposals_voted_against(self):
        """
        Returns a list (formerly QuerySet) of proposals that the user has voted against.
        """
        user_votes = Vote.objects.filter(user=self).filter(content_type=Proposal.contentType()).filter(isVoteUp=False)
        return [vote.content for vote in user_votes]
        #user_votes = Vote.objects.filter(user=self).filter(content_type=Proposal.contentType).filter(isVoteUp=False)
        #return Proposal.objects.filter(votes__in=user_votes)

    def __unicode__(self):
        return self.username + " (" + self.sid + ")"

class HideAction (models.Model):
    id = models.AutoField(primary_key=True)
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL)
    createdAt = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=2000)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey()

    def save(self, *args, **kwargs):
        if not self.moderator.isModerator:
            raise Exception("Only moderators may perform hide actions!")
        else:
            super(HideAction, self).save()
            content.isHidden = True
            content.save()

    @staticmethod
    def get_hide_actions(object_id, content_type):
        return HideAction.objects.filter(content_type=content_type, object_id=object_id)


class Report (models.Model):
    id = models.AutoField(primary_key=True)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL)
    createdAt = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=2000)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey()

    @staticmethod
    def get_reports(content):
        content_type = ContentType.objects.get_for_model(content)
        return Report.objects.filter(content_type=content_type, object_id=content.id)


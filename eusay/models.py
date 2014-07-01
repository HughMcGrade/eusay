'''
Created on 18 Feb 2014

@author: Hugh
'''
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
import datetime


class Comment (models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=500) # TODO: is this a good length? implement client-side character count
    createdAt = models.DateTimeField(auto_now_add=True)
    lastModified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey("User")
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

class Proposal (models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    actionDescription = models.CharField(max_length=2000)
    backgroundDescription = models.CharField(max_length=2000)
    beliefsDescription = models.CharField(max_length=2000)
    proposer = models.ForeignKey("User")#, related_name="proposed")
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    lastModified = models.DateTimeField(auto_now=True)

    def _get_votes_count(self, isUp):
        try:
            return len(ProposalVote.objects.all().filter(proposal=self).filter(isVoteUp = isUp))
        except Exception:
            return 0
    
    def get_votes_up_count(self):
        return self._get_votes_count(True)
    
    def get_votes_down_count(self):
        return self._get_votes_count(False)
    
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
    def get_proposals():
        return sorted([p for p in Proposal.objects.all() if not p.is_hidden()], key = lambda p: p.get_score())
    
class ProposalVote (Vote):
    proposal = models.ForeignKey(Proposal, related_name="votes")
    
class CommentVote (Vote):
    comment = models.ForeignKey(Comment, related_name="votes")
    
class User (models.Model):
    sid = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)
    createdAt = models.DateTimeField(default=datetime.datetime.now, editable=False)
    candidateStatus = models.CharField(max_length=20)
    isModerator = models.BooleanField(default=False)

    def save(self):
        if not self.sid:
            self.createdAt = datetime.datetime.now()
        super(User, self).save()


class HideAction (models.Model):
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

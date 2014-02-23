'''
Created on 18 Feb 2014

@author: Hugh
'''
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
import datetime

class Comment (models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=500)
    date = models.DateTimeField()
    user = models.ForeignKey("User")
    field = models.CharField(max_length=20, null=False)
    proposal = models.ForeignKey("Proposal", null=False)
    
    def _get_votes_count(self, isUp):
        try:
            return len(CommentVote.objects.all().filter(comment=self).filter(isVoteUp=isUp))
        except Exception:
            return 0
            
    def get_votes_up_count(self):
        return self._get_votes_count(True)
        
    def get_votes_down_count(self):
        return self._get_votes_count(False)

class Vote (models.Model):
    id = models.AutoField(primary_key=True)
    isVoteUp = models.BooleanField()
    date = models.DateTimeField()
    user = models.ForeignKey("User")
    
class Proposal (models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    actionDescription = models.CharField(max_length=2000)
    backgroundDescription = models.CharField(max_length=2000)
    beliefsDescription = models.CharField(max_length=2000)
    proposer = models.ForeignKey("User")#, related_name="proposed")
    submissionDateTime = models.DateField(null = True)
    
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
    
    def getScore(self):
        score = 0
        comments = Comment.objects.all().filter(proposal=self)
        for comment in comments:
            score += self._weight_instance(hour_age = self._hours_since(comment.date)) * 4
        
        votes = ProposalVote.objects.all().filter(proposal=self)
        for vote in votes:
            if vote.isVoteUp:
                score += self._weight_instance(hour_age = self._hours_since(vote.date)) * 2
            else:
                score += self._weight_instance(hour_age = self._hours_since(vote.date)) * 1
        
        vote_up_count = self.get_votes_up_count()
        return score * self._proximity_coefficient() + (vote_up_count - self.get_votes_down_count())
    
class ProposalVote (Vote):
    proposal = models.ForeignKey(Proposal)
    
class CommentVote (Vote):
    comment = models.ForeignKey(Comment)
    
class User (models.Model):
    sid = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)
    signUpDate = models.DateField()
    candidateStatus = models.CharField(max_length=20)
    
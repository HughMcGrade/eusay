'''
Created on 18 Feb 2014

@author: Hugh
'''
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class Comment (models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=500)
    date = models.DateField()
    user = models.ForeignKey("User")
    field = models.CharField(max_length=20, null=False)
    proposal = models.ForeignKey("Proposal", null=False)

class Vote (models.Model):
    id = models.AutoField(primary_key=True)
    isVoteUp = models.BooleanField()
    date = models.DateField()
    user = models.ForeignKey("User")
    
class Proposal (models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    actionDescription = models.CharField(max_length=2000)
    backgroundDescription = models.CharField(max_length=2000)
    beliefsDescription = models.CharField(max_length=2000)
    proposer = models.ForeignKey("User")#, related_name="proposed")
    
    def _getVotes(self, isUp):
        try:
            return len(ProposalVote.objects.all().filter(proposal=self).filter(isVoteUp = isUp))
        except Exception:
            return 0
    
    def votesUp(self):
        return self._getVotes(True)
    
    def votesDown(self):
        return self._getVotes(False)
    
class ProposalVote (Vote):
    proposal = models.ForeignKey(Proposal)
    
class CommentVote (Vote):
    comment = models.ForeignKey(Comment)
    
class User (models.Model):
    sid = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)
    signUpDate = models.DateField()
    candidateStatus = models.CharField(max_length=20)
    
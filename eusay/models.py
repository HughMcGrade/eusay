'''
Created on 18 Feb 2014

@author: Hugh
'''
from django.db import models

class Comment (models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=500)
    date = models.DateField()
    user = models.ForeignKey("User")

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
    comments = models.ForeignKey(Comment, null=True, blank=True)
    proposer = models.ForeignKey("User")#, related_name="proposed")
    
    def getVotes(self, isUp):
        try:
            return len(ProposalVote.objects.all().filter(proposal=self).filter(isVoteUp = isUp))
        except Exception:
            return 0
    
    def votesUp(self):
        return self.getVotes(True)
    
    def votesDown(self):
        return self.getVotes(False)
    
class ProposalVote (Vote):
    proposal = models.ForeignKey(Proposal)
    
class CommentVote (Vote):
    comment = models.ForeignKey(Comment)
    
class User (models.Model):
    sid = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)
    signUpDate = models.DateField()
    candidateStatus = models.CharField(max_length=20)
    
'''
Created on 18 Feb 2014

@author: Hugh
'''
from django.db import models

class Comment (models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=500)
    date = models.DateField()
    user = models.ForeignKey("User")#, related_name="votedForComment")

class Vote (models.Model):
    id = models.AutoField(primary_key=True)
    isVoteUp = models.BooleanField()
    date = models.DateField()
    user = models.ForeignKey("User")#, related_name="votedFor")
    
class Proposal (models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    actionDescription = models.CharField(max_length=2000)
    backgroundDescription = models.CharField(max_length=2000)
    beliefsDescription = models.CharField(max_length=2000)
    votes = models.ForeignKey(Vote, null=True, blank=True)
    comments = models.ForeignKey(Comment, null=True, blank=True)
    proposer = models.ForeignKey("User")#, related_name="proposed")
    
    def votesUp(self):
        return len(self.votes.filter(isVoteUp = True))
    
    def votesDown(self):
        return len(self.votes.filter(isVoteUp = False))
    
class ProposalVote (Vote):
    proposal = models.ForeignKey(Proposal, null=True)
    
class CommentVote (Vote):
    comment = models.ForeignKey(Comment, null=True)
    
class User (models.Model):
    sid = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)
    votedFor = models.ForeignKey(Vote, null=True, blank=True, related_name="Vote.user")
    commented = models.ForeignKey(Comment, null=True, blank=True, related_name="Comment.user")
    proposed = models.ForeignKey(Proposal, null=True, blank=True, related_name="Proposal.proposer")
    signUpDate = models.DateField()
    candidateStatus = models.CharField(max_length=20)
    
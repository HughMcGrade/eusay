'''
Created on 18 Feb 2014

@author: Hugh
'''

from django.shortcuts import render
from django.http import HttpResponse

from eusay.models import User, CommentVote, Proposal, ProposalVote, Vote, Comment
import datetime

def add_user(url_data):
    user = User()
    user.name = "John"
    user.sid = "s1234567"
    user.signUpDate = datetime.datetime.now()
    user.candidateStatus = "None"
    user.save()
    return HttpResponse("Hello")

def get_users(url_data):
    users = User.objects.all()
    s = ""
    for user in users:
        s = s + user.name + ", "
    return HttpResponse(s)
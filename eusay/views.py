'''
Created on 18 Feb 2014

@author: Hugh
'''

from django.template.loader import render_to_string
from django.shortcuts import render
from django.http import HttpResponse

from eusay.models import User, CommentVote, Proposal, ProposalVote, Vote, Comment
import datetime

def add_user(request):
    user = User()
    user.name = "John"
    user.sid = "s1234567"
    user.signUpDate = datetime.datetime.now()
    user.candidateStatus = "None"
    user.save()
    return HttpResponse(user.name + " added.")

def get_users(request):
    users = User.objects.all()
    s = ""
    for user in users:
        s = s + user.name + ", "
    return HttpResponse(s)

def index(request):
	return HttpResponse(render_to_string("index.html", {"users": User.objects.all()}))
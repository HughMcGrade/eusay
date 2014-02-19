'''
Created on 18 Feb 2014

@author: Hugh
'''

import datetime

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from eusay.forms import ProposalForm
from eusay.models import User, CommentVote, Proposal, ProposalVote, Vote, \
    Comment


def add_user(request):
    user = User()
    user.name = "Jim"
    user.sid = "s7654321"
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
    # TODO Get real user
    user = User.objects.all().first()
    
    return HttpResponse(render_to_string("index.html", {"proposals": Proposal.objects.all(), "user_votes" : user_proposal_votes_dict(user)}))

def submit(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ProposalForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            proposal = form.save(commit=False)
            proposal.proposer = User.objects.get(sid="s1234567")
            proposal.save()
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = ProposalForm() # An unbound form
        return render(request, 'submit.html', {'form': form})

def thanks(request):
    return HttpResponse(render_to_string("thanks.html"))

def proposal(request, proposalId):
    proposal = Proposal.objects.get(id=proposalId)
    return HttpResponse(render_to_string("proposal.html", {"proposal": proposal}))

def vote_proposal(request, ud, proposal_id):
    proposal = Proposal.objects.all().get(id=proposal_id)#get_object_or_404(Proposal, proposal_id)
    
    # TODO Get real user
    user = User.objects.all().first()
    
    # Check if they have already voted
    if ProposalVote.objects.all().filter(proposal=proposal).filter(user=user).count() == 1:
        # Has already voted
        previous_vote = ProposalVote.objects.all().filter(proposal=proposal).get(user=user)
        if previous_vote.isVoteUp and ud == "down":
            previous_vote.delete()
        elif not previous_vote.isVoteUp and ud == "up":
            previous_vote.delete()
        else:
            return HttpResponse("User has already voted")
    
    new_vote = ProposalVote()
    
    if ud == "up":
        new_vote.isVoteUp = True
    else:
        new_vote.isVoteUp = False
    
    new_vote.user = user
    new_vote.proposal = proposal
    new_vote.date = datetime.datetime.now()
    new_vote.save()
    return HttpResponse("Voted " + ud + " " + proposal_id + ". It now has " + str(proposal.votesUp()) + " votes up.")

def user_proposal_votes_dict(user):
    votes_dict = {}
    for proposal in Proposal.objects.all():
        try:
            vote = ProposalVote.objects.all().filter(proposal=proposal).get(user=user)
        except ObjectDoesNotExist:
            vote = None
        if vote == None:
            votes_dict[proposal.id] = 0
        elif vote.isVoteUp:
            votes_dict[proposal.id] = 1
        else:
            votes_dict[proposal.id] = -1
    return votes_dict

def vote_comment(request, ud, comment_id):
    comment = Comment.objects.all().get(id=comment_id)#get_object_or_404(Proposal, proposal_id)
    
    # TODO Get real user
    user = User.objects.all()[1]
    
    # Check if they have already voted
    if CommentVote.objects.all().filter(proposal=proposal).filter(user=user).count() == 1:
        # Has already voted
        previous_vote = CommentVote.objects.all().filter(comment=comment).get(user=user)
        if previous_vote.isVoteUp and ud == "down":
            previous_vote.delete()
        elif not previous_vote.isVoteUp and ud == "up":
            previous_vote.delete()
        else:
            return HttpResponse("User has already voted")
    
    new_vote = CommentVote()
    
    if ud == "up":
        new_vote.isVoteUp = True
    else:
        new_vote.isVoteUp = False
    
    new_vote.user = user
    new_vote.comment = comment
    new_vote.date = datetime.datetime.now()
    new_vote.save()
    
    return HttpResponse("Voted " + ud + " " + comment_id + ". It now has " + str(comment.votesUp()) + " votes up.")

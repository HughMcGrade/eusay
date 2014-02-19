'''
Created on 18 Feb 2014

@author: Hugh
'''

from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from eusay.forms import ProposalForm

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
    return HttpResponse(render_to_string("index.html", {"proposals": Proposal.objects.all()}))

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

def vote_up_proposal(request):
    # if the user typed the url directly in the browser's address bar
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        referer = "" # TODO Index
    
    proposal_id = request.GET.get('id')
    print(proposal_id)
    if proposal_id == None:
        proposal_id = 12345
    proposal = get_object_or_404(Proposal, proposal_id)
    
    new_vote = ProposalVote()
    new_vote.isVoteUp = True
    
    # TODO Get real user
    user = User.objects.all().first()
    
    new_vote.user = user
    new_vote.proposal = proposal
    new_vote.save()
    
    return HttpResponseRedirect(referer)

def vote_down_proposal(request):
    # if the user typed the url directly in the browser's address bar
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        referer = "" # TODO Index
    
    proposal_id = request.GET.get('id')
    proposal = get_object_or_404(Proposal, proposal_id)
    
    new_vote = ProposalVote()
    new_vote.isVoteUp = False
    
    # TODO Get real user
    user = User.objects.all().first()
    
    new_vote.user = user
    new_vote.proposal = proposal
    new_vote.save()
    
    return HttpResponseRedirect(referer)


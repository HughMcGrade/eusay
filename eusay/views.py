'''
Created on 18 Feb 2014

@author: Hugh
'''

import datetime

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string, get_template

from eusay.forms import ProposalForm, CommentForm
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
    
    return HttpResponse(render_to_string("index.html", {"proposals": Proposal.objects.all(), "type" : "proposal" }))
    
def about(request):
    return render(request, "about.html")

def submit(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ProposalForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            proposal = form.save(commit=False)
            proposal.proposer = User.objects.all()[0]
            proposal.submissionDateTime = datetime.datetime.now()
            proposal.save()
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = ProposalForm() # An unbound form
        return render(request, 'submit.html', {'form': form})

def thanks(request):
    return HttpResponse(render_to_string("thanks.html"))

def proposal(request, proposalId):
    # TODO Get real user
    user = User.objects.all()[0]
    
    proposal = Proposal.objects.get(id=proposalId)
    comments = Comment.objects.all().filter(proposal = proposal)
    action_comments = comments.filter(field = "action")
    background_comments = comments.filter(field = "background")
    beliefs_comments = comments.filter(field = "beliefs")

    if request.method == 'POST': # If the form has been submitted...
        form = CommentForm(request.POST) # A form bound to the POST data
        if "actionComment" in request.POST:
            commentType = "action"
        elif "backgroundComment" in request.POST:
            commentType = "background"
        elif "beliefsComment" in request.POST:
            commentType = "beliefs"

        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            comment = form.save(commit=False)
            comment.user = User.objects.all()[0]
            comment.date = datetime.datetime.now()
            comment.proposal = proposal
            comment.field = commentType
            comment.save()
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = CommentForm() # An unbound form
        return render(request, "proposal.html", {"form": form, "proposal": proposal, "action_comments" : action_comments, "background_comments" : background_comments, "beliefs_comments" : beliefs_comments, "user" : user})

    # return HttpResponse(render_to_string("proposal.html", {"proposal": proposal, "action_comments" : action_comments, "background_comments" : background_comments, "beliefs_comments" : beliefs_comments, "user" : user}))

def vote_proposal(request, ud, proposal_id):
    proposal = Proposal.objects.all().get(id=proposal_id)#get_object_or_404(Proposal, proposal_id)
    
    # TODO Get real user
    user = User.objects.all().first()
    
    # Check if they have already voted
    if ProposalVote.objects.all().filter(proposal=proposal).filter(user=user).count() == 1:
        # Has already voted
        previous_vote = ProposalVote.objects.all().filter(proposal=proposal).get(user=user)
        if ud == "get":
            if previous_vote.isVoteUp:
                user_vote = 1
            else:
                user_vote = -1
            print ("User vote for " + proposal_id +  " = " + str(user_vote))
            return render(request, "votes.html", { "object" : proposal, "user_vote" : user_vote, "type" : "proposal" })
        elif previous_vote.isVoteUp and ud == "down":
            # Toggle vote from up to down
            previous_vote.delete()
        elif not previous_vote.isVoteUp and ud == "up":
            # Toggle vote from down to up
            previous_vote.delete()
        else:
            # Cancel previous vote
            previous_vote.delete()
            return render(request, "votes.html", { "object" : proposal, "user_vote" : 0, "type" : "proposal" })
    
    if ud == "get":
        return render(request, "votes.html", { "object" : proposal, "user_vote" : 0, "type" : "proposal" })
    
    new_vote = ProposalVote()
    
    if ud == "up":
        new_vote.isVoteUp = True
        user_vote = 1
    else:
        new_vote.isVoteUp = False
        user_vote = -1
    
    new_vote.user = user
    new_vote.proposal = proposal
    new_vote.date = datetime.datetime.now()
    new_vote.save()
    
    return render(request, "votes.html", { "object" : proposal, "user_vote" : user_vote, "type" : "proposal" })
    #return HttpResponse("Voted " + ud + " " + proposal_id + ". It now has " + str(proposal.votesUp()) + " votes up.")

'''def user_proposal_votes_dict(user):
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
    return votes_dict'''

def vote_comment(request, ud, comment_id):
    comment = Comment.objects.all().get(id = comment_id)
    
    # TODO Get real user
    user = User.objects.all().first()
    
    # Check if they have already voted
    if CommentVote.objects.all().filter(comment = comment).filter(user = user).count() == 1:
        # Has already voted
        previous_vote = CommentVote.objects.all().filter(comment = comment).get(user = user)
        if ud == "get":
            if previous_vote.isVoteUp:
                user_vote = 1
            else:
                user_vote = -1
            return render(request, "votes.html", { "object" : comment, "user_vote" : user_vote, "type" : "comment" })
        elif previous_vote.isVoteUp and ud == "down":
            # Toggle vote from up to down
            previous_vote.delete()
        elif not previous_vote.isVoteUp and ud == "up":
            # Toggle vote from down to up
            previous_vote.delete()
        else:
            # Cancel previous vote
            previous_vote.delete()
            return render(request, "votes.html", { "object" : comment, "user_vote" : 0, "type" : "comment" })
    
    if ud == "get":
        return render(request, "votes.html", { "object" : comment, "user_vote" : 0, "type" : "comment" })
    
    new_vote = CommentVote()
    
    if ud == "up":
        new_vote.isVoteUp = True
        user_vote = 1
    else:
        new_vote.isVoteUp = False
        user_vote = -1
    
    new_vote.user = user
    new_vote.comment = comment
    new_vote.date = datetime.datetime.now()
    new_vote.save()
    
    return render(request, "votes.html", { "object" : comment, "user_vote" : user_vote, "type" : "comment" })

def post_comment(request, proposal_id, field):
    '''text = request.POST.get("text")
    user_sid = request.POST.get("user_sid")
    
    print (text)
    print (user_sid)
    
    comment = Comment()
    comment.text = text
    comment.user = User.objects.all().get(sid=user_sid)
    comment.date = datetime.datetime.now()
    comment.proposal = Proposal.objects.all().get(id=proposal_id)
    comment.field = field
    comment.save()'''
    
    form = CommentForm(request.POST) # A form bound to the POST data
    if "actionComment" in request.POST:
        commentType = "action"
    elif "backgroundComment" in request.POST:
        commentType = "background"
    elif "beliefsComment" in request.POST:
        commentType = "beliefs"

    if form.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data
        comment = form.save(commit=False)
        comment.user = User.objects.all()[0]
        comment.date = datetime.datetime.now()
        comment.proposal = proposal
        comment.field = commentType
        comment.save()
    else:
        # TODO Invalid comment?
        pass
    
    return get_comments(request, proposal_id, field)
    
    #return HttpResponse("Saved")
    
def get_comments(request, proposal_id, field):
    proposal = Proposal.objects.all().get(id = proposal_id)
    comments = Comment.objects.all().filter(proposal=proposal).filter(field=field)
    return HttpResponse(render_to_string("comments.html", { "comments" : comments }))

def get_comments_count(request, proposal_id, field):
    proposal = Proposal.objects.all().get(id = proposal_id)
    count = Comment.objects.all().filter(proposal=proposal).filter(field=field).count()
    return HttpResponse(str(count) + " comments")

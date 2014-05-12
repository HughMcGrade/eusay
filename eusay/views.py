'''
Created on 18 Feb 2014

@author: Hugh
'''

import datetime

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string

from eusay.forms import ProposalForm, CommentForm
from eusay.models import User, CommentVote, Proposal, ProposalVote, Vote, \
    Comment

import random
rand_names = ['Tonja','Kaley','Bo','Tobias','Jacqui','Lorena','Isaac','Adriene','Tuan','Shanon','Georgette','Chas','Yuonne','Michelina','Juliana','Odell','Juliet','Carli','Asha','Pearl','Kamala','Rubie','Elmer','Taren','Salley','Raymonde','Shelba','Alison','Wilburn','Katy','Denyse','Rosemary','Brooke','Carson','Tashina','Kristi','Aline','Yevette','Eden','Christoper','Juana','Marcie','Wendell','Vonda','Dania','Sheron','Meta','Frank','Thad','Cherise']
get_rand_name = lambda: rand_names[round((random.random() * 100) % 50)]

def _generate_new_user(request):
    user = User()
    user.name = get_rand_name()
    user.sid = "s" + str(int(str(User.objects.all().last().sid)[1:]) + 1)
    user.signUpDate = datetime.datetime.now()
    user.candidateStatus = "None"
    user.save()
    request.session['user_sid'] = user.sid
    return user

def get_current_user(request):
    user_sid = request.session.get('user_sid', None)
    if not user_sid:
        return _generate_new_user(request)
    else:
        return User.objects.get(sid=user_sid)

def add_user(request):
    user = _generate_new_user(request)
    return HttpResponse(user.name)

def get_users(request):
    users = User.objects.all()
    s = "Current user is " + request.session.get('user_sid', 'None!') + "<br />"
    for user in users:
        s = s + user.name + ", "
    return HttpResponse(s)

def index(request):
    user = get_current_user(request)
    template = "index.html" # main HTML
    proposals_template = "index_proposals.html" # just the proposals
    proposals = sorted(Proposal.objects.all(), key = lambda p: p.get_score())
    proposals.reverse()
    context = {
        "proposals": proposals,
        "type" : "proposal",
        "user" :  user,
        "proposals_template": proposals_template,
    }
	# ajax requests only return the proposals, not the whole page
    if request.is_ajax():
        template = proposals_template
    return render(request, template, context)
    
def about(request):
    user = get_current_user(request)
    return render(request, "about.html", { 'user' : user})

def submit(request):
    user = get_current_user(request)
    if request.method == 'POST': # If the form has been submitted...
        form = ProposalForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            proposal = form.save(commit=False)
            proposal.proposer = user
            proposal.submissionDateTime = datetime.datetime.now()
            proposal.save()
            return HttpResponseRedirect('/proposal/'+str(proposal.id)) # Redirect after POST
    else:
        form = ProposalForm() # An unbound form
        return render(request, 'submit.html', {'form': form, 'user': user})

def thanks(request):
    return HttpResponse(render_to_string("thanks.html"))

def proposal(request, proposalId):
    user = get_current_user(request)
    proposal = Proposal.objects.get(id=proposalId)
    comments = Comment.objects.all().filter(proposal = proposal).filter(replyTo = None)

    # TODO duplication currently for graceful deprecation
    
    #if request.is_ajax():
    #    return render(request, "proposal_comments.html", {"proposal" : proposal, "comments" : comments, "user": user })

    if request.method == 'POST': # If the form has been submitted...
        form = CommentForm(request.POST) # A form bound to the POST data
        comment = form.save(commit=False)
        if 'reply_to' in request.POST and request.POST['reply_to']:
            # Comment is a reply
            comment.replyTo = Comment.objects.get(id = request.POST['reply_to'])
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            comment.user = user
            comment.date = datetime.datetime.now()
            comment.proposal = proposal
            comment.save()
            #return HttpResponseRedirect('/thanks/') # Redirect after POST
    
    form = CommentForm() # An unbound form
    return render(request, "proposal.html", {"form": form, "proposal": proposal, "comments" : comments, "user" : user, "comments_template" : "proposal_comments.html"})

def vote_proposal(request, ud, proposal_id):
    proposal = Proposal.objects.all().get(id=proposal_id)#get_object_or_404(Proposal, proposal_id)
    
    user = get_current_user(request)
    
    # Check if they have already voted
    if ProposalVote.objects.all().filter(proposal=proposal).filter(user=user).count() == 1:
        # Has already voted
        previous_vote = ProposalVote.objects.all().filter(proposal=proposal).get(user=user)
        if ud == "get":
            if previous_vote.isVoteUp:
                user_vote = 1
            else:
                user_vote = -1
            return render(request, "proposal_votes.html", { "proposal" : proposal, "user_vote" : user_vote, "user" : user })
        elif previous_vote.isVoteUp and ud == "down":
            # Toggle vote from up to down
            previous_vote.delete()
        elif not previous_vote.isVoteUp and ud == "up":
            # Toggle vote from down to up
            previous_vote.delete()
        else:
            # Cancel previous vote
            previous_vote.delete()
            return render(request, "proposal_votes.html", { "proposal" : proposal, "user_vote" : 0, "user" : user })
    
    if ud == "get":
        return render(request, "proposal_votes.html", { "proposal" : proposal, "user_vote" : 0, "user" : user })
    
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
    
    return render(request, "proposal_votes.html", { "proposal" : proposal, "user_vote" : user_vote, "user" : user })

def vote_comment(request, ud, comment_id):
    comment = Comment.objects.all().get(id = comment_id)
    user = get_current_user(request)
    # Check if they have already voted
    if CommentVote.objects.all().filter(comment = comment).filter(user = user).count() == 1:
        # Has already voted
        previous_vote = CommentVote.objects.all().filter(comment = comment).get(user = user)
        if ud == "get":
            # Get previous vote
            if previous_vote.isVoteUp:
                user_vote = 1
            else:
                user_vote = -1
            return render(request, "comment_votes.html", { "comment" : comment, "user_vote" : user_vote, "user" : user })
        elif previous_vote.isVoteUp and ud == "down":
            # Toggle vote from up to down
            previous_vote.delete()
        elif not previous_vote.isVoteUp and ud == "up":
            # Toggle vote from down to up
            previous_vote.delete()
        else:
            # Cancel previous vote
            previous_vote.delete()
            return render(request, "comment_votes.html", { "comment" : comment, "user_vote" : 0, "user" : user })
    
    if ud == "get":
        # Get hasn't voted
        return render(request, "comment_votes.html", { "comment" : comment, "user_vote" : 0, "user" : user })
    
    new_vote = CommentVote()
    if ud == "up":
        # Set up vote
        new_vote.isVoteUp = True
        user_vote = 1
    else:
        # Set down vote
        new_vote.isVoteUp = False
        user_vote = -1
    
    new_vote.user = user
    new_vote.comment = comment
    new_vote.date = datetime.datetime.now()
    new_vote.save()
    
    return render(request, "comment_votes.html", { "comment" : comment, "user_vote" : user_vote, "user" : user })

def get_comments(request, proposal_id, reply_to):
    proposal = Proposal.objects.all().get(id = proposal_id)
    comments = Comment.objects.all().filter(proposal=proposal)
    form = CommentForm() # An unbound form
    if reply_to:
        comments = comments.filter(replyTo = reply_to)
    return render(request, "proposal_comments.html", { "comments" : comments, "request" : request, "user" : get_current_user(request), 'form' : form })

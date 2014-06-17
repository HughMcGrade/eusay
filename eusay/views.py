'''
Created on 18 Feb 2014

@author: Hugh
'''

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string

from rest_framework import generics
from eusay.serializers import ProposalListSerializer, ProposalDetailSerializer, CommentDetailSerializer, CommentListSerializer
from haystack.query import SearchQuerySet
from haystack.views import SearchView, search_view_factory

from eusay.forms import ProposalForm, CommentForm, HideProposalActionForm, HideCommentActionForm
from eusay.models import User, CommentVote, Proposal, ProposalVote, Vote, \
    Comment, HideCommentAction, HideProposalAction

import random
rand_names = ['Tonja','Kaley','Bo','Tobias','Jacqui','Lorena','Isaac','Adriene','Tuan','Shanon','Georgette','Chas','Yuonne','Michelina','Juliana','Odell','Juliet','Carli','Asha','Pearl','Kamala','Rubie','Elmer','Taren','Salley','Raymonde','Shelba','Alison','Wilburn','Katy','Denyse','Rosemary','Brooke','Carson','Tashina','Kristi','Aline','Yevette','Eden','Christoper','Juana','Marcie','Wendell','Vonda','Dania','Sheron','Meta','Frank','Thad','Cherise']
get_rand_name = lambda: rand_names[round((random.random() * 100) % 50)]

def _render_message(request, title, message):
    return render(request, "message.html", { "title" : title, "message" : message })

def _generate_new_user(request):
    user = User()
    user.name = get_rand_name()
    if not User.objects.all():
        user.sid = "s1"
    else:
        user.sid = "s" + str(int(str(User.objects.all().last().sid)[1:]) + 1)
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
    proposals = sorted([p for p in Proposal.objects.all() if not p.is_hidden()], key = lambda p: p.get_score())
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
    return render(request, "about.html", {'user': user})

def profile(request, user_id):
    current_user = _get_current_user(request)
    profile = User.objects.get(sid=user_id)
    return render(request, "profile.html", {'user': current_user, 'profile': profile})

def submit(request):
    user = get_current_user(request)
    if request.method == 'POST': # If the form has been submitted...
        form = ProposalForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            proposal = form.save(commit=False)
            proposal.proposer = user
            proposal.save()
            return HttpResponseRedirect('/proposal/'+str(proposal.id)) # Redirect after POST
        else:
            return HttpResponse(form.errors)
    else:
        form = ProposalForm() # An unbound form
        return render(request, 'submit.html', {'form': form, 'user': user})

def thanks(request):
    return HttpResponse(render_to_string("thanks.html"))

def proposal(request, proposalId):
    user = get_current_user(request)
    proposal = Proposal.objects.get(id=proposalId)
    '''
    # For sorted:
    comments = sorted([c for c in Comment.objects.all().filter(proposal = proposal).filter(replyTo = None) if not c.is_hidden()], key=lambda c: c.get_score())
    comments.reverse()
    '''
    comments = [c for c in Comment.objects.all().filter(proposal = proposal).filter(replyTo = None) if not c.is_hidden()]
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
            comment.proposal = proposal
            comment.save()
            #return HttpResponseRedirect('/thanks/') # Redirect after POST
    
    hide = None
    if proposal.is_hidden():
        hide = HideProposalAction.objects.all().get(proposal=proposal)

    form = CommentForm() # An unbound form
    return render(request, "proposal.html", {"form": form, "proposal": proposal, "comments" : comments, "user" : user, "comments_template" : "proposal_comments.html", "hide" : hide})

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
    new_vote.save()
    
    return render(request, "comment_votes.html", { "comment" : comment, "user_vote" : user_vote, "user" : user })

def get_comments(request, proposal_id, reply_to):
    proposal = Proposal.objects.all().get(id = proposal_id)
    form = CommentForm() # An unbound form
    if reply_to:
        '''
        # For sorted:
        comments = sorted([c for c in comments.filter(replyTo = reply_to) if not c.is_hidden()])
        comments.reverse()'''
        comments = [c for c in Comment.objects.all().filter(proposal=proposal).filter(replyTo = reply_to) if not c.is_hidden()]
    else:
        comments = [c for c in Comment.objects.all().filter(proposal=proposal) if not c.is_hidden()]
    return render(request, "proposal_comments.html", { "comments" : comments, "request" : request, "user" : get_current_user(request), 'form' : form })

def hide_comment(request, comment_id):
    user = get_current_user(request)
    if not user.isModerator:
        return _render_message(request, "Error", "Only moderators may hide comments")
    else:
        comment = Comment.objects.all().get(id = comment_id)
        if request.method == "POST":
            form = HideCommentActionForm(request.POST)
            if form.is_valid():
                hide_action = form.save(commit=False)
                hide_action.moderator = user
                hide_action.comment = comment
                hide_action.save()
                return _render_message(request, "Hidden", "The comment has been hidden and the hide action logged")
            else:
                # TODO Could improve handling of invalid form, though it is unlikely here
                return _render_message(request, "Error", "Invalid hide comment form")
        form = HideCommentActionForm()
        return render(request, "hide_comment_form.html", { "comment" : comment, "form" : form })

def hide_proposal(request, proposal_id):
    user = get_current_user(request)
    if not user.isModerator:
        return _render_error(request, "Only moderators may hide proposals")
    else:
        proposal = Proposal.objects.all().get(id = proposal_id)
        if request.method == "POST":
            form = HideProposalActionForm(request.POST)
            if form.is_valid():
                hide_action = form.save(commit=False)
                hide_action.moderator = user
                hide_action.proposal = proposal
                hide_action.save()
                return _render_message(request, "Hidden", "The proposal has been hidden and the hide action logged")
            else:
                # TODO Could improve handling of invalid form, though it is unlikely here
                return _render_message(request, "Error", "Invalid hide proposal form")
        form = HideProposalActionForm()
        return render(request, "hide_proposal_form.html", { "proposal" : proposal, "form" : form })

def comment_hides(request):
    hiddens = HideCommentAction.objects.all()
    return render(request, "hidden_comment_list.html", { "hiddens" : hiddens })

def proposal_hides(request):
    hiddens = HideProposalAction.objects.all()
    return render(request, "hidden_proposal_list.html", { "hiddens" : hiddens })


# def get_similar_proposals(request):

def search(request):
    user = get_current_user(request)
    query = str(request.GET.get("q"))

    results = SearchQuerySet().all().filter(content=query)
    view = search_view_factory(
        view_class=SearchView,
        searchqueryset=SearchQuerySet().all(),
        form_class="SearchForm"
    )
    return render(request, "search/search.html", {"user": user, "results": results})

# Temporary for debugging
def make_mod(request):
    user = get_current_user(request)
    user.isModerator = True
    user.save()
    return _render_message(request, "Temporary", "You are now a moderator")


class MultipleFieldLookupMixin(object):
    """
    Apply this mixin to any view or viewset to get multiple field filtering
    based on a `lookup_fields` attribute, instead of the default single field filtering.
    """
    def get_object(self):
        queryset = self.get_queryset()                  # Get the base queryset
        queryset = self.filter_queryset(queryset)       # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            filter[field] = self.kwargs[field]
        return get_object_or_404(queryset, **filter)    # Lookup the object


class ProposalList(generics.ListAPIView):
    """
    View a list of proposals.
    """
    queryset = Proposal.objects.all()
    serializer_class = ProposalListSerializer
    paginate_by = 5

class ProposalDetail(generics.RetrieveAPIView):
    """
    View a proposal's details.
    """
    queryset = Proposal.objects.all()
    serializer_class = ProposalDetailSerializer
    lookup_field = 'id' # proposal id


class CommentList(generics.ListAPIView):
    """
    View the comments of a specific proposal.
    """
    lookup_field = 'id' # proposal id
    serializer_class = CommentListSerializer
    def get_queryset(self):
        """
        This view should return a list of all the comments
        for a particular proposal.
        """
        proposalId = self.kwargs['id'] # kwarg from URL
        return Comment.objects.filter(proposal__id=proposalId)


class CommentDetail(generics.RetrieveAPIView):
    """
    View a single comment.
    """
    serializer_class = CommentDetailSerializer
    queryset = Comment.objects.all()
    lookup_field = 'id' # comment id
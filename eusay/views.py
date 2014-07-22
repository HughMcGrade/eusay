'''
Created on 18 Feb 2014

@author: Hugh
'''

from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseForbidden, HttpResponsePermanentRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from rest_framework import generics
from haystack.query import SearchQuerySet

from .forms import *
from .models import *
from .utils import better_slugify
from .serializers import ProposalListSerializer, ProposalDetailSerializer, CommentDetailSerializer,\
    CommentListSerializer

from django.contrib import messages

import random
import datetime

rand_names = ['Tonja','Kaley','Bo','Tobias','Jacqui','Lorena','Isaac','Adriene','Tuan','Shanon','Georgette','Chas','Yuonne','Michelina','Juliana','Odell','Juliet','Carli','Asha','Pearl','Kamala','Rubie','Elmer','Taren','Salley','Raymonde','Shelba','Alison','Wilburn','Katy','Denyse','Rosemary','Brooke','Carson','Tashina','Kristi','Aline','Yevette','Eden','Christoper','Juana','Marcie','Wendell','Vonda','Dania','Sheron','Meta','Frank','Thad','Cherise']
get_rand_name = lambda: rand_names[round((random.random() * 100) % 50) - 1]

# Do not use when using both AJAX and messages!
def _render_message_to_string(request, title, message):
    user = get_current_user(request)
    return render_to_string("message.html", { "title" : title, "message" : message, "user" : user })

def generate_new_user(request):
    user = User()
    user.name = get_rand_name()
    for u in User.objects.all():
        if u.name == user.name:
            user = u
    if not user.sid:
        if not User.objects.all():
            user.sid = "s1"
        else:
            user.sid = "s" + str(int(User.objects.all().last().sid[1:]) + 1)
        user.slug = better_slugify(user.name)
        user.save()
    request.session['user_sid'] = user.sid
    return user

def get_current_user(request):
    user_sid = request.session.get('user_sid', None)
    if not user_sid:
        return generate_new_user(request)
    else:
        return User.objects.get(sid=user_sid)

def add_user(request):
    user = generate_new_user(request)
    return HttpResponse(user.name)

# TODO: remove this, since it's for debugging
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
    proposals = Proposal.get_visible_proposals()
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

def profile(request, slug):
    current_user = get_current_user(request)
    profile = User.objects.get(slug=slug)
    if current_user == profile:
        # own profile
        if request.method == "POST":
            # if the form as been submitted
            form = UserForm(request.POST,
                            instance=current_user,
                            current_user=current_user)
            if form.is_valid():
                form.save()
                return redirect(reverse("user",
                                        kwargs={"slug": better_slugify(form.cleaned_data["name"], domain="User")}))
            else:
                errors = form.errors
                return render(request,
                              "own_profile.html",
                              {"user": current_user,
                               "profile": profile,
                               "form": form,
                               "errors": errors})
        form = UserForm(current_user=current_user) # unbound form
        return render(request,
                      "own_profile.html",
                      {'user': current_user,
                       'profile': profile,
                       'form': form})
    elif profile.hasProfile:
        # another's (public) profile
        return render(request,
                      "profile.html",
                      {'user': current_user,
                       'profile': profile})
    else:
        return render(request,
                      "no_profile.html",
                      {"user": current_user,
                       "profile": profile})

def submit(request):
    user = get_current_user(request)
    tags = Tag.objects.all()
    if request.method == 'POST': # If the form has been submitted...
        form = ProposalForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            proposal = form.save(commit=False)
            proposal.proposer = user
            proposal.save()
            return HttpResponseRedirect(
                reverse("proposal",
                        kwargs={"proposalId": proposal.id,
                                "slug": proposal.slug})) # Redirect after POST
        else:
            return HttpResponse(form.errors)
    else:
        form = ProposalForm() # An unbound form
        return render(request, 'submit.html', {'form': form,
                                               'user': user,
                                               "tags": tags})


def tag(request, tagId, slug):
    user = get_current_user(request)
    tag = Tag.objects.get(id=tagId)

    # redirect requests with the wrong slug to the correct page
    if not slug == tag.slug:
        return HttpResponsePermanentRedirect(tag.get_absolute_url())

    template = "tag.html" # main HTML
    proposals_template = "index_proposals.html" # just the proposals
    proposals = Proposal.get_visible_proposals(tag=tag)
    proposals.reverse()
    context = {
        "proposals": proposals,
        "user" :  user,
        "proposals_template": proposals_template,
        "tag": tag,
    }
    # ajax requests only return the proposals, not the whole page
    if request.is_ajax():
        template = proposals_template
    return render(request, template, context)


def proposal(request, proposalId, slug):
    user = get_current_user(request)
    proposal = Proposal.objects.get(id=proposalId)
    '''
    # For sorted:
    comments = sorted(proposal.get_visible_comments(), key=lambda c: c.get_score())
    comments.reverse()
    '''
    comments = proposal.get_visible_comments()
    # TODO duplication currently for graceful deprecation
    
    #if request.is_ajax():
    #    return render(request, "proposal_comments.html", {"proposal" : proposal, "comments" : comments, "user": user })

    # redirect requests with the wrong slug to the correct page
    if not slug == proposal.slug:
        return HttpResponsePermanentRedirect(proposal.get_absolute_url())

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

    hide = None
    if proposal.is_hidden():
        hide = HideProposalAction.objects.all().get(proposal=proposal)

    form = CommentForm() # An unbound form
    return render(request, "proposal.html", {"form": form, "proposal": proposal, "comments" : comments, "user" : user, "comments_template" : "proposal_comments.html", "hide" : hide})

def vote_proposal(request, vote_request_type, proposal_id):
    proposal = Proposal.objects.all().get(id=proposal_id)#get_object_or_404(Proposal, proposal_id)
    
    user = get_current_user(request)
    
    # Check if they have already voted
    if ProposalVote.objects.all().filter(proposal=proposal).filter(user=user).count() == 1:
        # Has already voted
        previous_vote = ProposalVote.objects.all().filter(proposal=proposal).get(user=user)
        if vote_request_type == "get":
            if previous_vote.isVoteUp:
                user_vote = 1
            else:
                user_vote = -1
            return render(request, "proposal_votes.html", { "proposal" : proposal, "user_vote" : user_vote, "user" : user })
        elif previous_vote.isVoteUp and vote_request_type == "down":
            # Toggle vote from up to down
            previous_vote.delete()
        elif not previous_vote.isVoteUp and vote_request_type == "up":
            # Toggle vote from down to up
            previous_vote.delete()
        else:
            # Cancel previous vote
            previous_vote.delete()
            return render(request, "proposal_votes.html", { "proposal" : proposal, "user_vote" : 0, "user" : user })
    
    if vote_request_type == "get":
        return render(request, "proposal_votes.html", { "proposal" : proposal, "user_vote" : 0, "user" : user })
    
    new_vote = ProposalVote()
    
    if vote_request_type == "up":
        new_vote.isVoteUp = True
        user_vote = 1
    else:
        new_vote.isVoteUp = False
        user_vote = -1
    
    new_vote.user = user
    new_vote.proposal = proposal
    new_vote.save()
    
    return render(request, "proposal_votes.html", { "proposal" : proposal, "user_vote" : user_vote, "user" : user })

def vote_comment(request, vote_request_type, comment_id):
    comment = Comment.objects.all().get(id = comment_id)
    user = get_current_user(request)
    # Check if they have already voted
    if CommentVote.objects.all().filter(comment = comment).filter(user = user).count() == 1:
        # Has already voted
        previous_vote = CommentVote.objects.all().filter(comment = comment).get(user = user)
        if vote_request_type == "get":
            # Get previous vote
            if previous_vote.isVoteUp:
                user_vote = 1
            else:
                user_vote = -1
            return render(request, "comment_votes.html", { "comment" : comment, "user_vote" : user_vote, "user" : user })
        elif previous_vote.isVoteUp and vote_request_type == "down":
            # Toggle vote from up to down
            previous_vote.delete()
        elif not previous_vote.isVoteUp and vote_request_type == "up":
            # Toggle vote from down to up
            previous_vote.delete()
        else:
            # Cancel previous vote
            previous_vote.delete()
            return render(request, "comment_votes.html", { "comment" : comment, "user_vote" : 0, "user" : user })
    
    if vote_request_type == "get":
        # Get hasn't voted
        return render(request, "comment_votes.html", { "comment" : comment, "user_vote" : 0, "user" : user })
    
    new_vote = CommentVote()
    if vote_request_type == "up":
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
    
    '''
        # For sorted:
        comments = sorted(proposal.get_visible_comments(reply_to))
        comments.reverse()'''
    if reply_to:
        comments = proposal.get_visible_comments(reply_to)
    else:
        comments = proposal.get_visible_comments()

    return render(request, "proposal_comments.html", { "comments" : comments, "request" : request, "user" : get_current_user(request), 'form' : form })

def hide_comment(request, comment_id):
    user = get_current_user(request)
    if not user.isModerator:
        return HttpResponseForbidden(_render_message_to_string(request, "Error", "Only moderators may hide comments"))
    else:
        comment = Comment.objects.all().get(id = comment_id)
        if request.method == "POST":
            form = HideCommentActionForm(request.POST)
            if form.is_valid():
                hide_action = form.save(commit=False)
                hide_action.moderator = user
                hide_action.comment = comment
                hide_action.save()
                return HttpResponse(_render_message_to_string(request, "Hidden", "The comment has been hidden and the hide action logged"))
            else:
                # TODO Could improve handling of invalid form, though it is unlikely here
                return HttpResponse(_render_message_to_string(request, "Error", "Invalid hide comment form"))
        form = HideCommentActionForm()
        return render(request, "hide_comment_form.html", { "comment" : comment, "form" : form })

def hide_proposal(request, proposal_id):
    user = get_current_user(request)
    if not user.isModerator:
        return HttpResponseForbidden(_render_message_to_string(request, "Error", "Only moderators may hide proposals"))
    else:
        proposal = Proposal.objects.all().get(id = proposal_id)
        if request.method == "POST":
            form = HideProposalActionForm(request.POST)
            if form.is_valid():
                hide_action = form.save(commit=False)
                hide_action.moderator = user
                hide_action.proposal = proposal
                hide_action.save()
                return HttpResponse(_render_message_to_string(request, "Hidden", "The proposal has been hidden and the hide action logged."))
            else:
                # TODO Could improve handling of invalid form, though it is unlikely here
                return HttpResponse(_render_message_to_string(request, "Error", "Invalid hide proposal form"))
        form = HideProposalActionForm()
        return render(request, "hide_proposal_form.html", { "proposal" : proposal, "form" : form })

def hide_from_report(request, report_id):
    user = get_current_user(request)
    if CommentReport.objects.all().filter(id=report_id):
        # Comment report
        report = CommentReport.objects.get(id=report_id)
        hide_action = HideCommentAction()
        hide_action.moderator = user
        hide_action.reason = report.reason
        hide_action.comment_id = report.comment_id
        hide_action.save()
        report.delete()
        messages.add_message(request, messages.INFO, "Comment hidden")
    elif ProposalReport.objects.all().filter(id=report_id):
        # Proposal report
        report = ProposalReport.objects.all().get(id=report_id)
        hide_action = HideProposalAction()
        hide_action.moderator = user
        hide_action.reason = report.reason
        hide_action.proposal = report.proposal
        hide_action.save()
        report.delete()
        messages.add_message(request, messages.INFO, "Proposal hidden")
    else:
        # Report not found
        raise Report.DoesNotExist()

def ignore_report(request, report_id):
    user = get_current_user(request)
    if not user.isModerator:
        return HttpResponseForbidden(_render_message_to_string(request, "Error", "Only moderators may hide proposals"))
    else:
        try:
            report = Report.objects.get(id=report_id)
            report.delete()
            messages.add_message(request, messages.INFO, "Report ignored")
            return HttpResponse("Report ignored")
        except Report.DoesNotExist:
            return HttpResponseNotFound(_render_message_to_string(request, "Error", "Report not found"))

def comment_hides(request):
    user = get_current_user(request)
    hiddens = HideCommentAction.objects.all()
    return render(request, "hidden_comment_list.html", { "hiddens" : hiddens, "user": user })

def proposal_hides(request):
    user = get_current_user(request)
    hiddens = HideProposalAction.objects.all()
    return render(request, "hidden_proposal_list.html", { "hiddens" : hiddens, "user" : user })

def report_comment(request, comment_id):
    user = get_current_user(request)
    comment = Comment.objects.all().get(id = comment_id)
    if request.method == "POST":
        form = CommentReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = user
            report.comment = comment
            report.save()
            return HttpResponse(_render_message_to_string(request, "Reported", "Your report has been submitted to the moderators."))
        else:
            # TODO Could improve handling of invalid form, though it is unlikely here
            return HttpResponse(_render_message_to_string(request, "Error", "Invalid report comment form"))
    else:
        form = HideCommentActionForm()
        return render(request, "report_comment_form.html", { "comment" : comment, "form" : form, "user": user })

def report_proposal(request, proposal_id):
    user = get_current_user(request)
    proposal = Proposal.objects.all().get(id = proposal_id)
    if request.method == "POST":
        form = ProposalReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = user
            report.proposal = proposal
            report.save()
            return HttpResponse(_render_message_to_string(request, "Reported", "Your report has been submitted to the moderators."))
        else:
            # TODO Could improve handling of invalid form, though it is unlikely here
            return HttpResponse(_render_message_to_string(request, "Error", "Invalid report proposal form"))
    else:
        form = ProposalReportForm()
        return render(request, "report_proposal_form.html", { "proposal" : proposal, "form" : form, "user": user })

def moderator_panel(request):
    user = get_current_user(request)
    if not user.isModerator:
        messages.add_message(request, messages.ERROR, "Only moderators may access the moderator panel.")
        if request.is_ajax():
            return HttpResponseForbidden("")
        else:
            return HttpResponseForbidden(_render_message_to_string(request, "Error", "Only moderators may access the moderator panel."))
    
    if request.method == "POST":
        report = request.POST.get("report")
        action = request.POST.get("action")
        ajaxResponseType = HttpResponse
        if action == "Hide":
            try:
                hide_from_report(request, report)
            except Report.DoesNotExist:
                messages.add_message(request, messages.ERROR, "Report not found")
                ajaxResponseType = HttpResponseNotFound
        elif action == "Ignore":
            try:
                ignore_report(request, report)
            except Report.DoesNotExist:
                messages.add_message(request, messages.ERROR, "Report not found")
                ajaxResponseType = HttpResponseNotFound
        else:
            messages.add_message("Moderation action type not found")
            ajaxResponseType = HttpResponseNotFound
        if request.is_ajax():
            return ajaxResponseType("")
    
    comment_reports = CommentReport.objects.all()
    proposal_reports = ProposalReport.objects.all()
    return render(request, "moderator_panel.html", { "comment_reports" : comment_reports, "proposal_reports" : proposal_reports, "user" : user })

def search(request):
    user = get_current_user(request)
    if request.method == "GET":
        if "q" in request.GET:
            query = str(request.GET.get("q"))
            results = SearchQuerySet().all().filter(content=query)
    return render(request, "search/search.html", {"user": user, "results": results})


# Temporary for debugging
# TODO: remove this when users + mods are implemented
def make_mod(request):
    user = get_current_user(request)
    user.isModerator = True
    user.save()
    return HttpResponse(_render_message_to_string(request, "Temporary", "You are now a moderator"))

def remove_comment(request, comment_id):
    comment = Comment.objects.all().get(id=comment_id)
    if comment.user == get_current_user(request):
        if len(comment.get_replies()) > 0:
            comment.user = User.objects.all()[0] # TODO Deleted comment user
            comment.text = "Comment deleted by user"
            comment.createdAt = datetime.datetime.now()
            comment.lastModified = datetime.datetime.now()
            comment.save()
            return HttpResponse("Comment cleared")
        else:
            comment.delete()
            return HttpResponse("Comment removed")
    else:
        return HttpResponseForbidden("Users may only remove their own comments")

def get_messages(request):
    return render(request, "get_messages.html")

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
    lookup_field = 'id'  # proposal id


class CommentList(generics.ListAPIView):
    """
    View the comments of a specific proposal.
    """
    lookup_field = 'id'  # proposal id
    serializer_class = CommentListSerializer

    def get_queryset(self):
        """
        This view should return a list of all the comments
        for a particular proposal.
        """
        proposalId = self.kwargs['id']  # kwarg from URL
        return Comment.objects.filter(proposal__id=proposalId)


class CommentDetail(generics.RetrieveAPIView):
    """
    View a single comment.
    """
    serializer_class = CommentDetailSerializer
    queryset = Comment.objects.all()
    lookup_field = 'id'  # comment id


class SearchResults(generics.ListAPIView):
    serializer_class = ProposalListSerializer
    paginate_by = 5
    def get_queryset(self):
        """
        Return search results.
        """
        def to_queryset(searchqueryset):
            """
            This helper function converts a SearchQuerySet (from the search)
            into a QuerySet.
            We don't use a generator here because pagination requires that you can
            take the len() of a list, a generators don't have a len().
            """
            return [item.object for item in searchqueryset]

        queryset = Proposal.objects.none()  # empty queryset by default
        query = self.request.QUERY_PARAMS.get('q')
        if query:
            queryset = to_queryset(SearchQuerySet().all().filter(content=query))
        return queryset

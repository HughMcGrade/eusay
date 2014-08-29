from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseForbidden, HttpResponsePermanentRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model

from lxml.html.diff import htmldiff

from proposals.forms import ProposalForm, ResponseForm, AmendmentForm
from comments.forms import CommentForm
from proposals.models import Proposal, Response
from comments.models import Comment
from tags.models import Tag
from users.views import request_login
from moderation.models import HideAction
from votes.views import do_vote

def index(request):
    template = "index.html" # main HTML
    proposals_template = "proposal_list.html" # just the proposals

    # sort by popularity by default
    proposals = Proposal.objects.get_visible_proposals(sort="popular")
    sort = "popular"

    if request.GET.get("sort") == "newest":
        proposals = Proposal.objects.get_visible_proposals(sort="newest")
        sort = "newest"

    context = {
        "proposals": proposals,
        "type" : "proposal",
        "proposals_template": proposals_template,
        "sort": sort,
    }

    if request.is_ajax() and 'page' in request.GET:
        # AJAX request for pagination
        template = proposals_template

    return render(request, template, context)

def submit(request):
    if not request.user.is_authenticated():
        return request_login(request)
    tags = Tag.objects.all()
    if request.method == 'POST':  # If the form has been submitted...
        form = ProposalForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            proposal = form.save(commit=False)
            proposal.user = request.user
            proposal.save()
            form.save_m2m()  # save tags
            return HttpResponseRedirect(
                reverse("proposal",
                        kwargs={"proposalId": proposal.id,
                                "slug": proposal.slug})) # Redirect after POST
        else:
            errors = form.errors
            return render(request, "submit.html", {"form": form,
                                                   "tags": tags,
                                                   "errors": errors})
    else:
        form = ProposalForm() # An unbound form
        return render(request, 'submit.html', {'form': form,
                                               "tags": tags})

def proposal(request, proposalId, slug=None):
    proposal = Proposal.objects.get(id=proposalId)

    response_headers = dict()

    # redirect requests with the wrong slug to the correct page
    if not slug == proposal.slug:
        return HttpResponsePermanentRedirect(proposal.get_absolute_url())

    user_vote = None
    if request.method == 'POST': # If the form has been submitted...
        if not request.user.is_authenticated():
            return request_login(request)
        if 'request' in request.POST:
            if request.POST['request'] == 'proposal_vote':
                vote_request = request.POST['vote']
                user_vote = do_vote(request.user, proposal, vote_request)
            elif request.POST['request'] == 'comment_vote':
                vote_string = request.POST['vote']
                # Parse vote
                if vote_string[0:2] == 'up':
                    comment_id = int(vote_string[2:])
                    response_headers['Comment-Id'] = str(comment_id)
                    comment = Comment.objects.get(id=comment_id)
                    do_vote(request.user, comment, 'up')
                elif vote_string[0:4] == 'down':
                    comment_id = int(vote_string[4:])
                    response_headers['Comment-Id'] = str(comment_id)
                    comment = Comment.objects.get(id=comment_id)
                    do_vote(request.user, comment, 'down')
                else:
                    raise Exception('Unknown vote string ' + vote_string)
            else:
                raise Exception('Unknown POST request '\
                                + request.POST['request'])
            proposal = Proposal.objects.get(id=proposalId)
        else:
            form = CommentForm(request.POST)
            comment = form.save(commit=False)
            if 'reply_to' in request.POST and request.POST['reply_to']:
                # Comment is a reply
                comment.replyTo = Comment.objects\
                                         .get(id=request.POST['reply_to'])
                response_headers['Comment-Id'] = request.POST['reply_to']
            if form.is_valid(): # All validation rules pass
                # Process the data in form.cleaned_data
                comment.user = request.user
                comment.proposal = proposal
                comment.save()

    hide = None
    if proposal.isHidden:
        hide = HideAction.objects.get(object_id=proposal.id,
                                      content_type=Proposal.get_content_type())

    if request.user.is_authenticated() and not user_vote:
        user_vote = request.user.get_vote_on(proposal)

    form = CommentForm()
    comments = proposal.get_visible_comments()
    context = {"form": form,
               "proposal": proposal,
               "comments": comments,
               "user_vote": user_vote,
               "hide": hide}

    comment_votes = {}
    if request.user.is_authenticated():
        comment_votes["comments_voted_for"] = \
            Comment.objects.filter(votes__user=request.user,
                                   votes__isVoteUp=True)
        comment_votes["comments_voted_against"] = \
            Comment.objects.filter(votes__user=request.user,
                                   votes__isVoteUp=False)

    context.update(comment_votes)

    response = render(request,
                      "proposal.html",
                      context)
    for key in response_headers:
        response[key] = response_headers[key]

    return response

def respond_to_proposal(request, proposalId, *args, **kwargs):
    if not request.user.is_authenticated():
        return request_login(request)
    if request.user.userStatus != "Staff"\
       and request.user.userStatus != "Officeholder":
        messages.add_message(request, messages.ERROR,
                             "Regular users cannot respond to proposals.")
        return HttpResponseRedirect(reverse('frontpage'))
    proposal = Proposal.objects.get(id=proposalId)
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.user = request.user
            response.proposal = proposal
            response.save()
            return HttpResponseRedirect(reverse('proposal',
                                                args=[str(proposal.id),
                                                      proposal.slug]))
        else:
            messages.add_message(request, messages.ERROR,
                                 "Invalid response form")
    form = ResponseForm()
    return render(request,
                  "respond_to_proposal_form.html",
                  {"proposal": proposal, "form": form})


def amend_proposal(request, proposal_id):
    if not request.user.is_authenticated():
        return request_login(request)
    proposal = Proposal.objects.get(id=proposal_id)
    if request.method == 'POST':
        if request.POST['action'] == 'view':
            amended_title = request.POST['title']
            amended_text = request.POST['text']

            diff = ""
            if amended_title != proposal.title:
                title_diff = htmldiff(proposal.title, amended_title)
                # Make title h1 with markdown
                diff += '**Title: ' + title_diff + '**\n'
            if amended_text != proposal.text:
                text_diff = htmldiff(proposal.text, amended_text)
                diff += text_diff

            form = AmendmentForm()
            form.set_initial(amended_title, amended_text)
            return render(request, "amend_proposal.html",
                          {'proposal' : proposal, 'form' : form,
                           'diff' : diff})
        elif request.POST['action'] == 'post':
            comment = Comment()
            comment.proposal = proposal
            comment.user = request.user
            comment.text = request.POST['text']
            comment.isAmendment = True
            comment.save()
            return HttpResponseRedirect(reverse('proposal',
                                                args=[proposal_id,
                                                      proposal.slug])
                                        + "#comment_" + str(comment.id))
        else:
            raise Exception('Unknown form action')
    else:
        form = AmendmentForm()
        form.set_initial(proposal.title, proposal.text)
        return render(request, "amend_proposal.html",
                      {'proposal' : proposal, 'form' : form})


def delete_proposal(request, proposal_id):
    if not request.user.is_authenticated():
        return request_login(request)
    proposal = Proposal.objects.get(id=proposal_id)
    if proposal.user != request.user:
        messages.add_message(request, messages.ERROR, ("You may only delete"
                                                       "your own proposals."
                                                       "Please submit a report"
                                                       "to request another"
                                                       "user's proposal be"
                                                       "hidden."))
        return HttpResponseRedirect(reverse('frontpage'))
    if request.method == 'POST':
        if request.POST['action'] == 'delete':
            proposal.text = "This proposal has been deleted by its proposer."
            proposal.title = "Deleted proposal"
            proposal.user = get_user_model().objects.get_deleted_content_user()
            proposal.tags.clear()
            proposal.save()
            messages.add_message(request, messages.INFO, "Proposal deleted")
            return HttpResponseRedirect(reverse("proposal",
                                                kwargs={"proposalId" :
                                                        proposal.id, "slug":
                                                        proposal.slug}))
    else:
        return render(request, 'delete_proposal.html', {'proposal' : proposal})

from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect,\
    Http404, HttpResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from haystack.query import SearchQuerySet

from lxml.html.diff import htmldiff
from itertools import chain

from proposals.forms import ProposalForm, ResponseForm, AmendmentForm,\
    ProposalStatusForm
from comments.forms import CommentForm
from proposals.models import Proposal, Response
from comments.models import Comment
from tags.models import Tag
from users.views import request_login
from moderation.models import HideAction
from votes.views import do_vote
from core.utils import to_queryset


def index(request):
    template = "index.html"  # main HTML
    proposals_template = "proposal_list.html"  # just the proposals

    # sort by popularity by default
    proposals = Proposal.objects.get_visible_proposals(sort="popular")
    sort = "popular"

    if request.GET.get("sort") == "newest":
        proposals = Proposal.objects.get_visible_proposals(sort="newest")
        sort = "newest"

    context = {
        "proposals": proposals,
        "type": "proposal",
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
            tags = list(chain(form.cleaned_data.get("school_tags"),
                              form.cleaned_data.get("liberation_tags"),
                              form.cleaned_data.get("other_tags")))
            proposal.tags.add(*tags)
            return HttpResponseRedirect(
                reverse("share",
                        kwargs={"proposal_id": proposal.id}))
        else:
            errors = form.errors
            return render(request, "submit.html", {"form": form,
                                                   "tags": tags,
                                                   "errors": errors})
    else:
        form = ProposalForm()  # An unbound form
        return render(request, 'submit.html', {'form': form,
                                               "tags": tags})


def proposal(request, proposal_id, slug=None):
    try:
        proposal = Proposal.objects.get(id=proposal_id)
    except:
        raise Http404

    response_headers = dict()

    # redirect requests with the wrong slug to the correct page
    if not slug == proposal.slug:
        return HttpResponsePermanentRedirect(proposal.get_absolute_url())

    user_vote = None
    if request.method == 'POST':  # If the form has been submitted...
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
                raise Exception('Unknown POST request '
                                + request.POST['request'])
            proposal = Proposal.objects.get(id=proposal_id)
        else:
            form = CommentForm(request.POST)
            comment = form.save(commit=False)
            if 'reply_to' in request.POST and request.POST['reply_to']:
                # Comment is a reply
                comment.replyTo = Comment.objects\
                                         .get(id=request.POST['reply_to'])
                response_headers['Comment-Id'] = request.POST['reply_to']
                response_headers['Is-Reply'] = 'True'
            if form.is_valid():  # All validation rules pass
                # Process the data in form.cleaned_data
                comment.user = request.user
                comment.proposal = proposal
                comment.save()
                if not 'Is-Reply' in response_headers:
                    response_headers['Comment-Id'] = str(comment.id)

    hide = None
    if proposal.isHidden:
        hide = HideAction.objects.get(object_id=proposal.id,
                                      content_type=Proposal.get_content_type())

    if request.user.is_authenticated() and not user_vote:
        user_vote = request.user.get_vote_on(proposal)

    similar_proposals = to_queryset(
        SearchQuerySet().more_like_this(proposal))[:3]
    new_proposals = Proposal.objects.get_visible_proposals()\
                            .exclude(id=proposal_id).order_by("-createdAt")[:3]

    form = CommentForm()
    comments = proposal.get_visible_comments()
    context = {"form": form,
               "proposal": proposal,
               "comments": comments,
               "user_vote": user_vote,
               "hide": hide,
               "similar_proposals": similar_proposals,
               "new_proposals": new_proposals}

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

def edit_proposal(request, proposal_id):
    try:
        proposal = Proposal.objects.get(id=proposal_id)
    except:
        raise Http404
    if not request.user.is_authenticated():
        return request_login()
    if request.user != proposal.user:
        messages.add_message(request,
                             messages.ERROR,
                             "You can't edit other people's proposals!")
        return HttpResponseRedirect(reverse("frontpage"))
    else:
        if request.method == "POST":
            if proposal.is_new():
                form = ProposalForm(request.POST, instance=proposal)
                if form.is_valid():
                    form.save()
                    messages.add_message(request, messages.SUCCESS,
                                         "Proposal edited.")
                    return HttpResponseRedirect(reverse("proposal", args=[
                                                        str(proposal.id),
                                                        proposal.slug]))
                else:
                    messages.add_message(request,
                                         messages.ERROR,
                                         "Invalid proposal.")
            else:
                messages.add_message(request, messages.ERROR,
                                     "You can only edit a proposal in the "
                                     "first hour.")

        form = ProposalForm(instance=proposal)
        if proposal.is_new():
            if request.is_ajax():
                extend_template = "ajax_base.html"
            else:
                extend_template = "base.html"
            return render(request, "edit_proposal_form.html",
                          {"form": form,
                           "proposal": proposal,
                           "extend_template": extend_template})
        else:
            messages.add_message(request, messages.ERROR,
                                 "You can only edit a proposal in the "
                                 "first hour.")
            return HttpResponseRedirect(reverse("proposal", args=[
                                                str(proposal.id),
                                                proposal.slug]))



def respond_to_proposal(request, proposal_id, *args, **kwargs):
    if not request.user.is_authenticated():
        return request_login(request)
    if request.user.userStatus != "Staff"\
       and request.user.userStatus != "Officeholder":
        messages.add_message(request, messages.ERROR,
                             "Regular users cannot respond to proposals.")
        return HttpResponseRedirect(reverse('frontpage'))
    try:
        proposal = Proposal.objects.get(id=proposal_id)
    except:
        raise Http404
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.user = request.user
            response.proposal = proposal
            response.save()
            return HttpResponseRedirect(reverse('proposal',
                                                kwargs={"proposal_id":
                                                        proposal.id, "slug":
                                                proposal.slug}))
        else:
            messages.add_message(request, messages.ERROR,
                                 "Invalid response form")
    form = ResponseForm()
    return render(request,
                  "respond_to_proposal_form.html",
                  {"proposal": proposal, "form": form})

def edit_response(request, response_id):
    if not request.user.is_authenticated():
        return request_login(request)
    try:
        response = Response.objects.get(id=response_id)
    except:
        raise Http404
    if not response.user == request.user:
        messages.add_message(request,
                             messages.ERROR,
                             "You can only edit your own responses.")
        return HttpResponseRedirect(reverse("proposal",
                                            args=[str(response.proposal.id)]))
    else:
        if request.method == "POST":
            form = ResponseForm(request.POST, instance=response)
            if form.is_valid():
                form.save()
                messages.add_message(request,
                                     messages.SUCCESS,
                                     "Response edited.")
                return HttpResponseRedirect(reverse("proposal", args=[
                    str(response.proposal.id)]))
            else:
                messages.add_message(request,
                                     messages.ERROR,
                                     "Invalid response")
        form = ResponseForm(instance=response)
        if request.is_ajax():
            extend_template = "ajax_base.html"
        else:
            extend_template = "base.html"
        return render(request,
                      "edit_response_form.html",
                      { "form": form,
                        "response": response,
                        "extend_template": extend_template })



def amend_proposal(request, proposal_id):
    if not request.user.is_authenticated():
        return request_login(request)
    try:
        proposal = Proposal.objects.get(id=proposal_id)
    except:
        raise Http404
    if request.is_ajax():
        extend_template = "ajax_base.html"
    else:
        extend_template = "base.html"
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
                          {'proposal': proposal, 'form': form,
                           'diff': diff, 'extend_template': extend_template})
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
                      {'proposal': proposal, 'form': form,
                       'extend_template': extend_template})


def delete_proposal(request, proposal_id):
    if not request.user.is_authenticated():
        return request_login(request)
    if request.is_ajax():
        extend_template = "ajax_base.html"
    else:
        extend_template = "base.html"
    try:
        proposal = Proposal.objects.get(id=proposal_id)
    except:
        raise Http404
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
            if proposal.comments.count() > 0:
                proposal.text = "This proposal has been deleted by its proposer."
                proposal.title = "Deleted proposal"
                proposal.user = get_user_model().objects.get_deleted_content_user()
                proposal.tags.clear()
                proposal.save()
                messages.add_message(request, messages.INFO, "Proposal deleted")
                return HttpResponseRedirect(reverse("proposal",
                                                    kwargs={"proposal_id":
                                                            proposal.id, "slug":
                                                            proposal.slug}))
            else:
                proposal.delete()
                messages.add_message(request, messages.INFO, "Proposal deleted")
                return HttpResponseRedirect(reverse("frontpage"))
    else:
        return render(request, 'delete_proposal.html',
                      {'proposal': proposal,
                       "extend_template": extend_template})


def update_proposal_status(request, proposal_id):
    if not request.user.is_authenticated():
        return request_login(request)
    if not request.user.userStatus == "Staff"\
       or request.user.userStatus == "Officeholder":
        messages.add_message(request, messages.ERROR, "You don't have "
                                                      "permission to do this.")
        return HttpResponseRedirect(reverse("frontpage"))
    try:
        proposal = Proposal.objects.get(id=proposal_id)
    except:
        raise Http404

    if request.method == "POST":
        print("form submitted.")
        form = ProposalStatusForm(request.POST, instance=proposal)
        if form.is_valid():
            form.save()
        else:
            messages.add_message(request, messages.ERROR, form.errors)
        return HttpResponseRedirect(reverse("proposal",
                                            kwargs={"proposal_id": proposal.id,
                                                    "slug": proposal.slug}))
    else:
        form = ProposalStatusForm(instance=proposal)
        return render(request, "update_proposal_status.html",
                      {"form": form, "proposal": proposal})


def share(request, proposal_id):
    try:
        proposal = Proposal.objects.get(id=proposal_id)
    except:
        raise Http404
    proposal_url = request.build_absolute_uri(proposal.get_absolute_url())
    return HttpResponse(render(request, "share.html",
                               {"proposal": proposal,
                                "proposal_url": proposal_url}))

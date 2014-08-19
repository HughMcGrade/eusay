'''
Created on 18 Feb 2014

@author: Hugh
'''

from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseForbidden, HttpResponsePermanentRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth import authenticate as django_authenticate, \
    login as django_login, logout as django_logout
from django.core.urlresolvers import reverse
from django.contrib import messages

from .forms import *
from .models import *
from .utils import better_slugify

import random
import datetime
from lxml.html.diff import htmldiff


rand_names = ['Tonja','Kaley','Bo','Tobias','Jacqui','Lorena','Isaac','Adriene','Tuan','Shanon','Georgette','Chas','Yuonne','Michelina','Juliana','Odell','Juliet','Carli','Asha','Pearl','Kamala','Rubie','Elmer','Taren','Salley','Raymonde','Shelba','Alison','Wilburn','Katy','Denyse','Rosemary','Brooke','Carson','Tashina','Kristi','Aline','Yevette','Eden','Christoper','Juana','Marcie','Wendell','Vonda','Dania','Sheron','Meta','Frank','Thad','Cherise']
get_rand_name = lambda: random.choice(rand_names)

def request_login(request):
    messages.add_message(request, messages.INFO, "You must be logged in to do this")
    return HttpResponseRedirect(reverse('frontpage'))

def generate_new_user(request):
    username = get_rand_name()
    if User.objects.filter(username__exact=username).exists():
        user = User.objects.get(username=username)
    else:
        if User.objects.exclude(sid__exact="").exclude(sid__exact="Deleted Content").count() == 0:
            # if there are no users with sids, give sid "s1"
            sid = "s1"
        else:
            previous_sid = User.objects.all().exclude(sid__exact="Deleted Content").last().sid
            previous_sid_num = previous_sid[1:]
            new_sid_num = int(previous_sid_num) + 1
            sid = "s" + str(new_sid_num)
        user = User.objects.create_user(username=username, password="", sid=sid)
        user.slug = better_slugify(user.username)
        user.save()
    user = django_authenticate(username=user.username, password="")
    if user is not None:
        django_login(request, user)
        return user
    else:
        raise Exception("User is None!")


def add_user(request):
    user = generate_new_user(request)
    return HttpResponse(user.username)

# TODO: remove this, since it's for debugging
def get_users(request):
    users = User.objects.all()
    s = "Current user is " + request.user.username + "<br />"
    for user in users:
        s = s + user.username + ", "
    return HttpResponse(s)

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
    
    #ajax requests only return the proposals, not the whole page
    if request.is_ajax() and 'page' in request.GET:
        template = proposals_template
    
    return render(request, template, context)

def about(request):
    return render(request, "about.html")

def profile(request, slug):
    profile = User.objects.get(slug=slug)
    if request.user == profile:
        # own profile
        if request.method == "POST":
            # if the form as been submitted
            form = UserForm(request.POST,
                            instance=request.user,
                            current_user=request.user)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse("user",
                                        kwargs={"slug": better_slugify(form.cleaned_data["username"], domain="User")}))
            else:
                messages.add_message(request,
                                     messages.ERROR,
                                     "That username is unavailable.")
                # error_msg = "That username is unavailable."
                return render(request,
                              "own_profile.html",
                              {"profile": profile,
                               "form": form
                               #"error_msg": error_msg
                               })
        form = UserForm(current_user=request.user) # unbound form
        return render(request,
                      "own_profile.html",
                      {'profile': profile,
                       'form': form})
    elif profile.hasProfile:
        # another's (public) profile
        return render(request,
                      "profile.html",
                      {'profile': profile})
    else:
        return render(request,
                      "no_profile.html",
                      {"profile": profile})

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


def tag(request, tagId, slug):
    tag = Tag.objects.get(id=tagId)

    # redirect requests with the wrong slug to the correct page
    if not slug == tag.slug:
        return HttpResponsePermanentRedirect(tag.get_absolute_url())

    template = "tag.html" # main HTML
    proposals_template = "proposal_list.html" # just the proposals

    # sort by popularity by default
    proposals = Proposal.objects.get_visible_proposals(tag=tag, sort="popular")
    sort = "popular"

    if request.GET.get("sort") == "newest":
        proposals = Proposal.objects.get_visible_proposals(tag=tag, sort="newest")
        sort = "newest"

    context = {
        "proposals": proposals,
        "proposals_template": proposals_template,
        "tag": tag,
        "sort": sort,
    }
    # TODO if we find the JS approach is okay, change this:
    # ajax requests only return the proposals, not the whole page
    if request.is_ajax():
        template = proposals_template
    return render(request, template, context)

def do_vote(user, content, vote_request):
    try:
        content_type = ContentType.objects.get_for_model(content)
        vote = Vote.objects.all().get(user=user, object_id=content.id, content_type=content_type)
        # Test for cancel vote
        if (vote_request == "up" and vote.isVoteUp) or (vote_request == "down" and not vote.isVoteUp):
            vote.delete()
            return 0
    except Vote.DoesNotExist:
        vote = Vote(user=user, content=content)
    
    if vote_request == "up":
        vote.isVoteUp = True
        vote.save()
        return 1
    elif vote_request == "down":
        vote.isVoteUp = False
        vote.save()
        return -1
    else:
        raise Exception("Unknown vote request " + str(vote_request))

def proposal(request, proposalId, slug=None):
    proposal = Proposal.objects.get(id=proposalId)
    
    # TODO duplication currently for graceful deprecation
    
    #if request.is_ajax():
    #    return render(request, "proposal_comments.html", {"proposal" : proposal, "comments" : comments, "user": user })

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
                    comment = Comment.objects.all().get(id=comment_id)
                    do_vote(request.user, comment, 'up')
                elif vote_string[0:4] == 'down':
                    comment_id = int(vote_string[4:])
                    response_headers['Comment-Id'] = str(comment_id)
                    comment = Comment.objects.all().get(id=comment_id)
                    do_vote(request.user, comment, 'down')
                else:
                    raise Exception('Unknown vote string ' + vote_string)
            else:
                raise Exception('Unknown POST request ' + request.POST['request'])
            proposal = Proposal.objects.get(id=proposalId)
        else:
            form = CommentForm(request.POST) # A form bound to the POST data
            comment = form.save(commit=False)
            if 'reply_to' in request.POST and request.POST['reply_to']:
                # Comment is a reply
                comment.replyTo = Comment.objects.get(id = request.POST['reply_to'])
                response_headers['Comment-Id'] = request.POST['reply_to']
            if form.is_valid(): # All validation rules pass
                # Process the data in form.cleaned_data
                comment.user = request.user
                comment.proposal = proposal
                comment.save()

    hide = None
    if proposal.isHidden:
        hide = HideAction.objects.all().get(object_id=proposal.id, content_type=Proposal.contentType())

    if request.user.is_authenticated() and not user_vote:
        user_vote = request.user.get_vote_on(proposal)

    form = CommentForm() # An unbound form
    
    '''
    # For sorted:
    comments = sorted(proposal.get_visible_comments(), key=lambda c: c.get_score())
    comments.reverse()
    '''
    comments = proposal.get_visible_comments()
    
    response = render(request,
                  "proposal.html",
                  {"form": form,
                   "proposal": proposal,
                   "comments": comments,
                   "user_vote": user_vote,
                   #"comments_template": "proposal_comments.html",
                   "hide": hide})
    for key in response_headers:
        response[key] = response_headers[key]

    return response

def hide_comment(request, comment_id):
    if not request.user.is_authenticated():
        return request_login(request)
    elif not request.user.isModerator:
        messages.add_message(request,
                             messages.ERROR,
                             "Only moderators may perform hide actions.")
        return HttpResponseRedirect(reverse('frontpage'))
    else:
        comment = Comment.objects.all().get(id = comment_id)
        if request.method == "POST":
            form = HideActionForm(request.POST)
            if form.is_valid():
                hide_action = form.save(commit=False)
                hide_action.moderator = request.user
                hide_action.content = comment
                hide_action.save()
                messages.add_message(request, messages.INFO, "The comment has been hidden and hide action logged")
                return HttpResponseRedirect(reverse('frontpage'))
            else:
                messages.add_message(request, messages.ERROR, "Invalid hide comment form")
        form = HideActionForm()
        return render(request, "hide_comment_form.html", {"comment": comment,
                                                          "form": form})


def edit_comment(request, comment_id):
    if not request.user.is_authenticated():
        return request_login(request)
    comment = Comment.objects.get(id=comment_id)
    if not request.user == comment.user:
        messages.add_message(request,
                             messages.ERROR,
                             "You can only edit your own comments.")
        return HttpResponseRedirect(reverse('proposal',
                                            args=[
                                                str(comment.proposal.id),
                                                comment.proposal.slug
                                            ]))
    else:
        if request.method == "POST":
            if comment.is_new():
                form = CommentForm(request.POST, instance=comment)
                if form.is_valid():
                    form.save()
                    messages.add_message(request,
                                         messages.SUCCESS,
                                         "Comment edited.")
                    return HttpResponseRedirect(reverse("proposal", args=[
                        str(comment.proposal.id), comment.proposal.slug
                    ]))
                else:
                    messages.add_message(request,
                                         messages.ERROR,
                                         "Invalid comment.")
            else:
                messages.add_message(request,
                                     messages.ERROR,
                                     "You can only edit a comment in the "
                                     "first 5 minutes.")
        form = CommentForm(instance=comment)
        if comment.is_new():
            return render(request,
                          "edit_comment_form.html",
                          {"form": form,
                           "comment": comment})
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 "You can only edit a comment in the "
                                 "first 5 minutes.")
            return HttpResponseRedirect(reverse("proposal", args=[
                str(comment.proposal.id), comment.proposal.slug
            ]))


def hide_proposal(request, proposal_id):
    if not request.user.is_authenticated():
        return request_login(request)
    if not request.user.isModerator:
        messages.add_message(request, messages.ERROR, "Only moderators may perform hide actions.")
        return HttpResponseRedirect(reverse('frontpage'))
    else:
        proposal = Proposal.objects.all().get(id = proposal_id)
        if request.method == "POST":
            form = HideActionForm(request.POST)
            if form.is_valid():
                hide_action = form.save(commit=False)
                hide_action.moderator = request.user
                hide_action.content = proposal
                hide_action.save()
                messages.add_message(request, messages.INFO, "The proposal has been hidden and hide action logged")
                return HttpResponseRedirect(reverse('frontpage'))
            else:
                messages.add_message(request, messages.ERROR, "Invalid hide proposal form")
        form = HideActionForm()
        return render(request,
                      "hide_proposal_form.html",
                      {"proposal": proposal,
                       "form": form})

def comment_hides(request):
    hiddens = HideAction.objects.all().filter(content_type=Comment.contentType())
    return render(request, "hidden_comment_list.html", { "hiddens" : hiddens})

def proposal_hides(request):
    hiddens = HideAction.objects.all().filter(content_type=Proposal.contentType())
    return render(request, "hidden_proposal_list.html", { "hiddens" : hiddens})

def report_comment(request, comment_id):
    comment = Comment.objects.all().get(id = comment_id)
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            if request.user.is_authenticated():
                report.reporter = request.user
            report.content = comment
            report.save()
            messages.add_message(request, messages.INFO, "Your report has been submitted to the moderators.")
            return HttpResponseRedirect(reverse('frontpage'))
        else:
            messages.add_message(request, messages.ERROR, "Invalid report comment form")
    else:
        form = ReportForm()
        return render(request, "report_comment_form.html", { "comment" : comment, "form" : form})

def report_proposal(request, proposal_id):
    proposal = Proposal.objects.all().get(id = proposal_id)
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            if request.user.is_authenticated():
                report.reporter = request.user
            report.content = proposal
            report.save()
            messages.add_message(request, messages.INFO, "Your report has been submitted to the moderators.")
            return HttpResponseRedirect(reverse('frontpage'))
        else:
            messages.add_message(request, messages.ERROR, "Invalid report proposal form")
    else:
        form = ReportForm()
        return render(request, "report_proposal_form.html", { "proposal" : proposal, "form" : form})


def respond_to_proposal(request, proposalId, *args, **kwargs):
    if not request.user.is_authenticated():
        return request_login(request)
    if request.user.userStatus != "Staff" and request.user.userStatus != "Officeholder":
        messages.add_message(request, messages.ERROR, "Regular users cannot respond to proposals.")
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
            messages.add_message(request, messages.ERROR, "Invalid response form")
    form = ResponseForm()
    return render(request,
                  "respond_to_proposal_form.html",
                  {"proposal": proposal, "form": form})


def moderator_panel(request):
    if not request.user.is_authenticated():
        return request_login(request)
    if not request.user.isModerator:
        messages.add_message(request, messages.ERROR, "Only moderators may access the moderator panel.")
        if request.is_ajax():
            return HttpResponseForbidden("")
        else:
            return HttpResponseRedirect(reverse('frontpage'))
    
    if request.method == "POST":
        report_id = request.POST.get("report")
        report = Report.objects.get(id=report_id)
        action = request.POST.get("action")
        ajaxResponseType = HttpResponse
        if action == "Hide":
            try:
                hide_action = HideAction()
                hide_action.moderator = request.user
                hide_action.reason = report.reason
                hide_action.content = report.content
                hide_action.save()
                report.delete()
                messages.add_message(request, messages.INFO, "Content hidden")
            except Report.DoesNotExist:
                messages.add_message(request, messages.ERROR, "Report not found")
                ajaxResponseType = HttpResponseNotFound
        elif action == "Ignore":
            try:
                report.delete()
                messages.add_message(request, messages.INFO, "Report ignored")
            except Report.DoesNotExist:
                messages.add_message(request, messages.ERROR, "Report not found")
                ajaxResponseType = HttpResponseNotFound
        else:
            messages.add_message("Moderation action type not found")
            ajaxResponseType = HttpResponseNotFound
        if request.is_ajax():
            return ajaxResponseType("")
    
    comment_reports = Report.objects.filter(content_type=Comment.contentType())
    proposal_reports = Report.objects.filter(content_type=Proposal.contentType())
    return render(request, "moderator_panel.html", { "comment_reports" : comment_reports, "proposal_reports" : proposal_reports})


# Temporary for debugging
# TODO: remove this when users + mods are implemented
def make_mod(request):
    if not request.user.is_authenticated():
        return request_login(request)
    request.user.isModerator = True
    request.user.save()
    messages.add_message(request, messages.INFO, "You are now a moderator")
    return HttpResponseRedirect(reverse('frontpage'))


def make_staff(request):
    if not request.user.is_authenticated():
        return request_login(request)
    request.user.userStatus = "Staff"
    request.user.save()
    messages.add_message(request, messages.INFO, "You are now EUSA Staff")
    return HttpResponseRedirect(reverse('frontpage'))

def get_messages(request):
    return render(request, "get_messages.html")

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
                diff += '**Title: ' + title_diff + '**\n'  # make title h1 with markdown
            if amended_text != proposal.text:
                text_diff = htmldiff(proposal.text, amended_text)
                diff += text_diff

            form = AmendmentForm()
            form.set_initial(amended_title, amended_text)
            return render(request, "amend_proposal.html", { 'proposal' : proposal, 'form': form, 'diff' : diff })
        elif request.POST['action'] == 'post':
            comment = Comment()
            comment.proposal = proposal
            comment.user = request.user
            comment.text = request.POST['text']
            comment.isAmendment = True
            comment.save()
            return HttpResponseRedirect(reverse('proposal', args=[proposal_id, proposal.slug]))
        else:
            raise Exception('Unknown form action')
    else:
        form = AmendmentForm()
        form.set_initial(proposal.title, proposal.text)
        return render(request, "amend_proposal.html", { 'proposal' : proposal, 'form' : form })

def delete_proposal(request, proposal_id):
    if not request.user.is_authenticated():
        return request_login(request)
    proposal = Proposal.objects.get(id=proposal_id)
    if proposal.user != request.user:
        messages.add_message(request, messages.ERROR, "You may only delete your own proposals. Please submit a report to request another user's proposal be hidden.")
        return HttpResponseRedirect(reverse('frontpage'))
    if request.method == 'POST':
        if request.POST['action'] == 'delete':
            proposal.text = "This proposal has been deleted by its proposer."
            proposal.title = "Deleted proposal"
            proposal.user = User.objects.get_deleted_content_user()
            proposal.tags.clear()
            proposal.save()
            messages.add_message(request, messages.INFO, "Proposal deleted")
            return HttpResponseRedirect(reverse("proposal", kwargs={"proposalId": proposal.id, "slug": proposal.slug}))
    else:
        return render(request, 'delete_proposal.html', { 'proposal' : proposal})

def delete_comment(request, comment_id):
    if not request.user.is_authenticated():
        return request_login(request)
    comment = Comment.objects.get(id=comment_id)
    if comment.user != request.user:
        messages.add_message(request,
                             messages.ERROR,
                             "You may only delete your own comments. "
                             "Please submit a report to request another "
                             "user's comment be hidden.")
        return HttpResponseRedirect(reverse('proposal',
                                            args=[
                                                str(comment.proposal.id),
                                                comment.proposal.slug
                                            ]))
    if request.method == 'POST':
        if request.POST['action'] == 'delete':
            comment.text = "This comment has been deleted by its creator."
            comment.user = User.objects.get_deleted_content_user()
            comment.save()
            messages.add_message(request, messages.SUCCESS, "Comment deleted")
            return HttpResponseRedirect(reverse("proposal", kwargs={"proposalId": comment.proposal.id, "slug": comment.proposal.slug}))
    else:
        return render(request, 'delete_comment.html', {'comment': comment})


def logout(request):
    if request.user.is_authenticated():
        # TODO: delete cosign cookie(s)
        django_logout(request)
        messages.add_message(request,
                             messages.SUCCESS,
                             "You have been logged out.")
    else:
        messages.add_message(request,
                             messages.ERROR,
                             "You can't log out if you aren't logged "
                             "in first!")
    return redirect(reverse("frontpage"))


def login(request):
    if request.user.is_authenticated():
        messages.add_message(request,
                             messages.ERROR,
                             "You are already logged in.")
    else:
        generate_new_user(request)
        messages.add_message(request,
                             messages.SUCCESS,
                             "You are now logged in.")
    return redirect(reverse("frontpage"))

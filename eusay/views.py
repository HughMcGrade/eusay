'''
Created on 18 Feb 2014

@author: Hugh
'''

from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseForbidden, HttpResponsePermanentRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from .forms import *
from .models import *
from .utils import better_slugify

from django.contrib import messages

import random
import datetime

from lxml.html.diff import htmldiff

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
    proposals_template = "proposal_list.html" # just the proposals

    # sort by popularity by default
    proposals = Proposal.get_visible_proposals(sort="popular")
    sort = "popular"

    if request.GET.get("sort") == "newest":
        proposals = Proposal.get_visible_proposals(sort="newest")
        sort = "newest"

    context = {
        "proposals": proposals,
        "type" : "proposal",
        "user" :  user,
        "proposals_template": proposals_template,
        "sort": sort,
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
                error_msg = "That username is unavailable."
                return render(request,
                              "own_profile.html",
                              {"user": current_user,
                               "profile": profile,
                               "form": form,
                               "error_msg": error_msg})
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
    if request.method == 'POST':  # If the form has been submitted...
        form = ProposalForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            proposal = form.save(commit=False)
            proposal.user = user
            proposal.save()
            form.save_m2m()  # save tags
            return HttpResponseRedirect(
                reverse("proposal",
                        kwargs={"proposalId": proposal.id,
                                "slug": proposal.slug})) # Redirect after POST
        else:
            errors = form.errors
            return render(request, "submit.html", {"form": form,
                                                   "user": user,
                                                   "tags": tags,
                                                   "errors": errors})
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
    proposals_template = "proposal_list.html" # just the proposals

    # sort by popularity by default
    proposals = Proposal.get_visible_proposals(tag=tag, sort="popular")
    sort = "popular"

    if request.GET.get("sort") == "newest":
        proposals = Proposal.get_visible_proposals(tag=tag, sort="newest")
        sort = "newest"

    context = {
        "proposals": proposals,
        "user":  user,
        "proposals_template": proposals_template,
        "tag": tag,
        "sort": sort,
    }
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

def proposal(request, proposalId, slug):
    user = get_current_user(request)
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
        if 'request' in request.POST:
            if request.POST['request'] == 'proposal_vote':
                vote_request = request.POST['vote']
                user_vote = do_vote(user, proposal, vote_request)
            elif request.POST['request'] == 'comment_vote':
                vote_string = request.POST['vote']
                # Parse vote
                if vote_string[0:2] == 'up':
                    comment_id = int(vote_string[2:])
                    response_headers['Comment-Id'] = str(comment_id)
                    comment = Comment.objects.all().get(id=comment_id)
                    do_vote(user, comment, 'up')
                elif vote_string[0:4] == 'down':
                    comment_id = int(vote_string[4:])
                    response_headers['Comment-Id'] = str(comment_id)
                    comment = Comment.objects.all().get(id=comment_id)
                    do_vote(user, comment, 'down')
                else:
                    raise Exception('Unknown vote string ' + vote_string)
            else:
                raise Exception('Unknown POST request ' + request.POST['request'])
        else:
            form = CommentForm(request.POST) # A form bound to the POST data
            comment = form.save(commit=False)
            if 'reply_to' in request.POST and request.POST['reply_to']:
                # Comment is a reply
                comment.replyTo = Comment.objects.get(id = request.POST['reply_to'])
                response_headers['Comment-Id'] = request.POST['reply_to']
            if form.is_valid(): # All validation rules pass
                # Process the data in form.cleaned_data
                comment.user = user
                comment.proposal = proposal
                comment.save()

    hide = None
    if proposal.is_hidden():
        hide = HideAction.objects.all().get(proposal=proposal)

    if not user_vote:
        user_vote = user.get_vote_on(proposal)

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
                   "user": user,
                   "user_vote": user_vote,
                   #"comments_template": "proposal_comments.html",
                   "hide": hide})
    for key in response_headers:
        response[key] = response_headers[key]

    return response

def vote_comment(request, vote_request_type, comment_id):
    comment = Comment.objects.all().get(id = comment_id)
    user = get_current_user(request)
    
    # Check already voted
    try:
        previous_vote = Vote.objects.all().get(user=user, content=comment)
        # Already voted
        if vote_request_type == "get":
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
    except Vote.DoesNotExist:
        pass
    
    if vote_request_type == "get":
        # Get hasn't voted
        return render(request, "comment_votes.html", { "comment" : comment, "user_vote" : 0, "user" : user })
    
    new_vote = Vote()
    if vote_request_type == "up":
        # Set up vote
        new_vote.isVoteUp = True
        user_vote = 1
    else:
        # Set down vote
        new_vote.isVoteUp = False
        user_vote = -1
    
    new_vote.user = user
    new_vote.content = comment
    new_vote.save()
    
    return render(request, "comment_votes.html", { "comment" : comment, "user_vote" : user_vote, "user" : user })

def hide_comment(request, comment_id):
    user = get_current_user(request)
    if not user.isModerator:
        return HttpResponseForbidden(_render_message_to_string(request, "Error", "Only moderators may hide comments"))
    else:
        comment = Comment.objects.all().get(id = comment_id)
        if request.method == "POST":
            form = HideActionForm(request.POST)
            if form.is_valid():
                hide_action = form.save(commit=False)
                hide_action.moderator = user
                hide_action.content = comment
                hide_action.save()
                return HttpResponse(_render_message_to_string(request, "Hidden", "The comment has been hidden and the hide action logged"))
            else:
                # TODO Could improve handling of invalid form, though it is unlikely here
                return HttpResponse(_render_message_to_string(request, "Error", "Invalid hide comment form"))
        form = HideActionForm()
        return render(request, "hide_comment_form.html", {"comment": comment,
                                                          "form": form,
                                                          "user": user})

def hide_proposal(request, proposal_id):
    user = get_current_user(request)
    if not user.isModerator:
        return HttpResponseForbidden(_render_message_to_string(request, "Error", "Only moderators may hide proposals"))
    else:
        proposal = Proposal.objects.all().get(id = proposal_id)
        if request.method == "POST":
            form = HideActionForm(request.POST)
            if form.is_valid():
                hide_action = form.save(commit=False)
                hide_action.moderator = user
                hide_action.content = proposal
                hide_action.save()
                return HttpResponse(_render_message_to_string(request, "Hidden", "The proposal has been hidden and the hide action logged."))
            else:
                # TODO Could improve handling of invalid form, though it is unlikely here
                return HttpResponse(_render_message_to_string(request, "Error", "Invalid hide proposal form"))
        form = HideActionForm()
        return render(request,
                      "hide_proposal_form.html",
                      {"proposal": proposal,
                       "form": form,
                       "user": user})

def hide_from_report(request, report):
    user = get_current_user(request)
    hide_action = HideAction()
    hide_action.moderator = user
    hide_action.reason = report.reason
    hide_action.content = report.content
    hide_action.save()
    report.delete()
    messages.add_message(request, messsages.INFO, "Content hidden")

def ignore_report(request, report):
    user = get_current_user(request)
    if not user.isModerator:
        return HttpResponseForbidden(_render_message_to_string(request, "Error", "Only moderators may hide proposals"))
    else:
        try:
            report.delete()
            messages.add_message(request, messages.INFO, "Report ignored")
            return HttpResponse("Report ignored")
        except Report.DoesNotExist:
            return HttpResponseNotFound(_render_message_to_string(request, "Error", "Report not found"))

def comment_hides(request):
    user = get_current_user(request)
    hiddens = HideAction.objects.all().filter(content_type=Comment.contentType())
    return render(request, "hidden_comment_list.html", { "hiddens" : hiddens, "user": user })

def proposal_hides(request):
    user = get_current_user(request)
    hiddens = HideAction.objects.all().filter(content_type=Proposal.contentType())
    return render(request, "hidden_proposal_list.html", { "hiddens" : hiddens, "user" : user })

def report_comment(request, comment_id):
    user = get_current_user(request)
    comment = Comment.objects.all().get(id = comment_id)
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = user
            report.content = comment
            report.save()
            return HttpResponse(_render_message_to_string(request, "Reported", "Your report has been submitted to the moderators."))
        else:
            # TODO Could improve handling of invalid form, though it is unlikely here
            return HttpResponse(_render_message_to_string(request, "Error", "Invalid report comment form"))
    else:
        form = ReportForm()
        return render(request, "report_comment_form.html", { "comment" : comment, "form" : form, "user": user })

def report_proposal(request, proposal_id):
    user = get_current_user(request)
    proposal = Proposal.objects.all().get(id = proposal_id)
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = user
            report.content = proposal
            report.save()
            return HttpResponse(_render_message_to_string(request, "Reported", "Your report has been submitted to the moderators."))
        else:
            # TODO Could improve handling of invalid form, though it is unlikely here
            return HttpResponse(_render_message_to_string(request, "Error", "Invalid report proposal form"))
    else:
        form = ReportForm()
        return render(request, "report_proposal_form.html", { "proposal" : proposal, "form" : form, "user": user })


def respond_to_proposal(request, proposalId, *args, **kwargs):
    user = get_current_user(request)
    proposal = Proposal.objects.get(id=proposalId)
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.user = user
            response.proposal = proposal
            response.save()
            return HttpResponseRedirect(reverse('proposal',
                                                args=[str(proposal.id),
                                                      proposal.slug]))
    else:
        form = ResponseForm()
        return render(request,
                      "respond_to_proposal_form.html",
                      {"proposal": proposal, "form": form, "user": user})


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
    
    comment_reports = Report.objects.filter(content_type=Comment.contentType())
    proposal_reports = Report.objects.filter(content_type=Proposal.contentType())
    return render(request, "moderator_panel.html", { "comment_reports" : comment_reports, "proposal_reports" : proposal_reports, "user" : user })


# Temporary for debugging
# TODO: remove this when users + mods are implemented
def make_mod(request):
    user = get_current_user(request)
    user.isModerator = True
    user.save()
    messages.add_message(request, messages.INFO, "You are now a moderator")
    return HttpResponseRedirect(reverse('frontpage'))


def make_staff(request):
    user = get_current_user(request)
    user.userStatus = "Staff"
    user.save()
    messages.add_message(request, messages.INFO, "You are now EUSA Staff")
    return HttpResponseRedirect(reverse('frontpage'))

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

def amend_proposal(request, proposal_id):
    proposal = Proposal.objects.get(id=proposal_id)
    user = get_current_user(request)
    if request.method == 'POST':
        if request.POST['action'] == 'view':
            amended_title = request.POST['title']
            amended_text = request.POST['text']

            diff = '**Proposed amendments**\n'
            if amended_title != proposal.title:
                title_diff = htmldiff(proposal.title, amended_title)
                diff = diff + '*Title:* ' + title_diff + '\n'
            if amended_text != proposal.text:
                text_diff = htmldiff(proposal.text, amended_text)
                diff = diff + '*Text:* ' + text_diff

            form = AmendmentForm()
            form.set_initial(amended_title, amended_text)
            return render(request, "amend_proposal.html", { 'proposal' : proposal, 'user' : user, 'form': form, 'diff' : diff })
        elif request.POST['action'] == 'post':
            comment = Comment()
            comment.proposal = proposal
            comment.user = user
            comment.text = request.POST['text']
            comment.save()
            return HttpResponseRedirect("/proposal/" + str(proposal_id) + '/' + proposal.slug)
        else:
            raise Exception('Unknown form action')
    else:
        form = AmendmentForm()
        form.set_initial(proposal.title, proposal.text)
        return render(request, "amend_proposal.html", { 'proposal' : proposal, 'user' : user, 'form' : form })

'''
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
'''

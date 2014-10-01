from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseForbidden, HttpResponseNotFound, Http404
from django.core.urlresolvers import reverse

from users.views import request_login
from moderation.forms import HideActionForm, ReportForm
from proposals.models import Proposal
from comments.models import Comment
from moderation.models import HideAction, Report


def hide_comment(request, comment_id):
    if not request.user.is_authenticated():
        return request_login(request)
    elif not request.user.isModerator:
        messages.add_message(request,
                             messages.ERROR,
                             "Only moderators may perform hide actions.")
        return HttpResponseRedirect(reverse('frontpage'))
    else:
        try:
            comment = Comment.objects.get(id=comment_id)
        except:
            raise Http404
        if request.method == "POST":
            form = HideActionForm(request.POST)
            if form.is_valid():
                hide_action = form.save(commit=False)
                hide_action.moderator = request.user
                hide_action.content = comment
                hide_action.save()
                messages.add_message(request, messages.INFO,
                                     ("The comment has been hidden "
                                      "and hide action logged"))
                return HttpResponseRedirect(reverse(
                    'proposal', kwargs={"proposal_id": comment.proposal.id,
                                        "slug": comment.proposal.slug}))
            else:
                messages.add_message(request, messages.ERROR,
                                     "Invalid hide comment form")
        if request.is_ajax():
            extend_template = "ajax_base.html"
        else:
            extend_template = "base.html"
        form = HideActionForm()
        return render(request, "hide_comment_form.html", {"comment": comment,
                                                          "form": form,
                                                          "extend_template":
                                                          extend_template})


def hide_proposal(request, proposal_id):
    if not request.user.is_authenticated():
        return request_login(request)
    if not request.user.isModerator:
        messages.add_message(request, messages.ERROR,
                             "Only moderators may perform hide actions.")
        return HttpResponseRedirect(reverse('frontpage'))
    else:
        try:
            proposal = Proposal.objects.get(id=proposal_id)
        except:
            raise Http404
        if request.method == "POST":
            form = HideActionForm(request.POST)
            if form.is_valid():
                hide_action = form.save(commit=False)
                hide_action.moderator = request.user
                hide_action.content = proposal
                hide_action.save()
                messages.add_message(request, messages.INFO,
                                     ("The proposal has been hidden and "
                                      "hide action logged"))
                return HttpResponseRedirect(reverse('frontpage'))
            else:
                messages.add_message(request, messages.ERROR,
                                     "Invalid hide proposal form")
        form = HideActionForm()
        if request.is_ajax():
            extend_template = "ajax_base.html"
        else:
            extend_template = "base.html"
        return render(request,
                      "hide_proposal_form.html",
                      {"proposal": proposal, "form": form,
                       "extend_template": extend_template})


def comment_hides(request):
    hiddens = HideAction.objects.all()\
                                .filter(
                                    content_type=Comment.get_content_type())
    return render(request, "hidden_comment_list.html", {"hiddens": hiddens})


def proposal_hides(request):
    hiddens = HideAction.objects.all()\
                                .filter(
                                    content_type=Proposal.get_content_type())
    return render(request, "hidden_proposal_list.html", {"hiddens": hiddens})


def report_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except:
        raise Http404
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            if request.user.is_authenticated():
                report.reporter = request.user
            report.content = comment
            report.save()
            messages.add_message(request, messages.INFO,
                                 ("Your report has been submitted "
                                  "to the moderators."))
            return HttpResponseRedirect(reverse('frontpage'))
        else:
            messages.add_message(request, messages.ERROR,
                                 "Invalid report comment form")
    else:
        if request.is_ajax():
            extend_template = "ajax_base.html"
        else:
            extend_template = "base.html"
        form = ReportForm()
        return render(request, "report_comment_form.html",
                      {"comment": comment, "form": form,
                       "extend_template": extend_template})


def report_proposal(request, proposal_id):
    try:
        proposal = Proposal.objects.get(id=proposal_id)
    except:
        raise Http404
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            if request.user.is_authenticated():
                report.reporter = request.user
            report.content = proposal
            report.save()
            messages.add_message(request, messages.INFO,
                                 ("Your report has been submitted to "
                                  "the moderators."))
            return HttpResponseRedirect(reverse('frontpage'))
        else:
            messages.add_message(request, messages.ERROR,
                                 "Invalid report proposal form")
    else:
        if request.is_ajax():
            extend_template = "ajax_base.html"
        else:
            extend_template = "base.html"
        form = ReportForm()
        return render(request, "report_proposal_form.html",
                      {"proposal": proposal, "form": form,
                       "extend_template": extend_template})


def moderator_panel(request):
    if not request.user.is_authenticated():
        return request_login(request)
    if not request.user.isModerator:
        messages.add_message(request, messages.ERROR,
                             "Only moderators may access the moderator panel.")
        if request.is_ajax():
            return HttpResponseForbidden("")
        else:
            return HttpResponseRedirect(reverse('frontpage'))

    if request.method == "POST":
        report_id = request.POST.get("report")
        report = Report.objects.get(id=report_id)
        action = request.POST.get("action")
        ajax_response_type = HttpResponse
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
                messages.add_message(request, messages.ERROR,
                                     "Report not found")
                ajax_response_type = HttpResponseNotFound
        elif action == "Ignore":
            try:
                report.delete()
                messages.add_message(request, messages.INFO,
                                     "Report ignored")
            except Report.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     "Report not found")
                ajax_response_type = HttpResponseNotFound
        else:
            messages.add_message(request, messages.ERROR,
                                 "Moderation action type not found")
            ajax_response_type = HttpResponseNotFound
        if request.is_ajax():
            return ajax_response_type("")

    comment_reports = Report.objects.filter(
        content_type=Comment.get_content_type())
    proposal_reports = Report.objects.filter(
        content_type=Proposal.get_content_type())
    return render(request, "moderator_panel.html",
                  {"comment_reports": comment_reports,
                   "proposal_reports": proposal_reports})

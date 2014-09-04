from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from comments.models import Comment
from comments.forms import CommentForm
from users.views import request_login


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
                    ]) + "#comment_" + str(comment.id))
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
            if request.is_ajax():
                extend_template = "ajax_base.html"
            else:
                extend_template = "base.html"
            return render(request,
                          "edit_comment_form.html",
                          {"form": form,
                           "comment": comment,
                           "extend_template": extend_template})
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 "You can only edit a comment in the "
                                 "first 5 minutes.")
            return HttpResponseRedirect(reverse("proposal", args=[
                str(comment.proposal.id), comment.proposal.slug
            ]) + "#comment_" + str(comment.id))


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
            comment.user = get_user_model().objects.get_deleted_content_user()
            comment.save()
            messages.add_message(request, messages.SUCCESS, "Comment deleted")
            return HttpResponseRedirect(reverse("proposal",
                                                kwargs={"proposal_id":
                                                        comment.proposal.id,
                                                        "slug":
                                                        comment.proposal.slug})
                                        + "#comment_" + str(comment.id))
    else:
        if request.is_ajax():
            extend_template = "ajax_base.html"
        else:
            extend_template = "base.html"
        return render(request, 'delete_comment.html', {'comment': comment,
                                                       "extend_template":
                                                       extend_template})

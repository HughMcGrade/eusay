from django.shortcuts import render

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
                form = forms.CommentForm(request.POST, instance=comment)
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
        form = forms.CommentForm(instance=comment)
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
            return HttpResponseRedirect(reverse("proposal",
                                                kwargs={"proposalId" :
                                                        comment.proposal.id,
                                                        "slug":
                                                        comment.proposal.slug}))
    else:
        return render(request, 'delete_comment.html', {'comment': comment})

from django import template
from eusay.models import CommentVote
from django.template.loader import render_to_string
from eusay.views import get_current_user
from eusay.forms import CommentForm

register = template.Library()

@register.filter(name='comment_user_vote')
def comment_user_vote(comment, user):
    try:
        vote = CommentVote.objects.all().filter(comment = comment).get(user = user)
    except Exception:
        vote = None
    if not vote:
        user_vote = 0
    elif vote.isVoteUp:
        user_vote = 1
    else:
        user_vote = -1
    return render_to_string('comment_votes.html', { 'comment' : comment, 'user_vote' : user_vote })

@register.filter(name='comment_replies')
def comment_replies(comment, request):
    user = get_current_user(request)
    form = CommentForm() # An unbound form
    return render_to_string('proposal_comments.html', { 'request' : request, 'comments': comment.get_replies(), 'user' : user, 'form' : form })

from django import template
from eusay.models import Vote
from django.template.loader import render_to_string
from django.template.defaultfilters import stringfilter, pluralize
from django.utils.safestring import mark_safe
from eusay.views import get_current_user
from eusay.forms import CommentForm
from django.conf import settings
import re
import markdown
import bleach
import datetime

register = template.Library()

@register.filter
def comment_user_vote(comment, user):
    try:
        vote = Vote.get_votes(comment).get(user = user)
    except Exception:
        vote = None
    if not vote:
        user_vote = 0
    elif vote.isVoteUp:
        user_vote = 1
    else:
        user_vote = -1
    return render_to_string('comment_votes.html', { 'comment' : comment, 'user_vote' : user_vote })

@register.filter
def comment_replies(comment):
    return comment.get_replies(sort="chronological")

@register.filter
@stringfilter
def replace_bad_words(value):
    #Replaces profanities in strings with safe words
    # For instance, "shit" becomes "s--t"
    words = re.sub("[^\w]", " ", value).split()
    bad_words_seen = []
    for word in words:
        if word.lower() in settings.PROFANITIES_LIST:
            bad_words_seen.append(word)
    if bad_words_seen:
        for word in bad_words_seen:
            value = value.replace(word, "%s%s%s" % (word[0], '-'*(len(word)-2), word[-1]))
    return value

@register.filter(is_safe=True)
@stringfilter
def my_markdown(text):
    extensions = ["nl2br", ]
    html = markdown.markdown(text, extensions=extensions)
    linkified = bleach.linkify(html)
    allowed_tags = bleach.ALLOWED_TAGS
    allowed_tags.append("ins")
    allowed_tags.append("del")
    cleaned_text = bleach.clean(linkified, strip_comments=False, tags=allowed_tags)
    return mark_safe(cleaned_text)


@register.filter(name="timesince_human")
def humanize_timesince(date):
    delta = datetime.datetime.now() - date

    num_years = delta.days // 365
    if num_years > 0:
        return u"%d year%s ago" % (num_years, pluralize(num_years))

    num_weeks = delta.days // 7
    if num_weeks > 0:
        return u"%d week%s ago" % (num_weeks, pluralize(num_weeks))

    if delta.days > 0:
        return u"%d day%s ago" % (delta.days, pluralize(delta.days))

    num_hours = delta.seconds // 3600
    if num_hours > 0:
        return u"%d hour%s ago" % (num_hours, pluralize(num_hours))

    num_minutes = delta.seconds // 60
    if num_minutes > 0:
        return u"%d minute%s ago" % (num_minutes, pluralize(num_minutes))

    return u"a few seconds ago"


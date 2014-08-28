"""The filters used in eusay templates"""
import re
import markdown
import bleach
import datetime

from django.template.loader import render_to_string
from django.template.defaultfilters import stringfilter, pluralize
from django.utils.safestring import mark_safe
from django import template
from django.conf import settings

from votes.models import Vote
from comments.forms import CommentForm
from core.utils import smart_truncate as core_smart_truncate

register = template.Library()

@register.filter
def comment_user_vote(comment, user):
    """Get the vote, or lack thereof, of ``user`` on ``comment``

    :returns: The vote of ``user`` on ``comment`` as ``0`` for no vote, ``-1``
    for down vote and ``1`` for up vote
    :rtype: integer

    """
    try:
        vote = comment.votes.get(user = user)
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
    """Get the replies to ``comment``

    :returns: Replies to ``comment`` sorted chronologically
    :rtype: QuerySet

    """
    return comment.get_replies(sort="chronological")

@register.filter
@stringfilter
def replace_bad_words(value):
    """Replace words in ``value`` found in ``settings.PROFANITIES_LIST`` with
    dashes

    :type value: string 
    :returns: ``value`` without profanities
    :rtype: string

    """
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
    """Custom markdown filter

    :param text: Text to render as markdown
    :returns: ``text`` rendered to markdown
    :rtype: string

    """
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
    """Converts ``date`` to a human readable string describing the time since

    :param date: Date to convert
    :returns: Time since string
    :rtype: string

    """
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


@register.filter
def smart_time(date):
    """Creates string describing ``date`` depending on relation to current
    time - hour and minute if ``date`` is today, day and month if ``date`` is
    this year and day, month and year if ``date`` was before this year.

    :rtype: string

    """
    delta = datetime.datetime.now() - date

    num_years = delta.days // 365
    if num_years > 0:
        return date.strftime("%d %b, %Y")

    elif date.date() != datetime.date.today():
        return date.strftime("%d %b")

    else:
        return date.strftime("%H:%M")


@register.filter
def smart_truncate(text):
    """
    Simply a filter for the smart_truncate function in core.utils
    :param text: the text to be truncated
    :rtype: string
    """
    return core_smart_truncate(text)
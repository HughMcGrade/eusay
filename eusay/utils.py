import re

from django.template.defaultfilters import slugify
from django.conf import settings


def better_slugify(text, **kwargs):
            # Most of our SlugFields have a max length of 100 characters, so
            # we make sure it doesn't exceed that.
            slug = slugify(text)[:100]

            def remove_last_word(value):
                # If there's more than one word, make sure that the slug
                # doesn't end in the middle of a word.
                if len(value.split("-")) > 1:
                    while (value[-1:] != "-") and (len(value) > 1):
                        value = value[:-1]
                    # Remove the final hyphen
                    value = value[:-1]
                return value

            remove_last_word(slug)
            return slug


def add_proposals(amount):
    """
    Add a bunch of (very!) generic proposals
    """
    from .models import User, Proposal
    if not amount:
        raise Exception

    for i in range(1, amount+1):
        user = User.objects.create(sid="s" + str(i), name=str(i))
        Proposal.objects.create(title=str(i),
                                text="Proposal by " + user.name,
                                proposer=user)


def to_queryset(searchqueryset):
    """
    This function converts a SearchQuerySet into a QuerySet.
    We don't use a generator here because pagination in the API requires
    that you can take the len() of a list, a generators don't have a len().
    """
    return [item.object for item in searchqueryset]


def contains_swear_words(text):
    words = re.sub("[^\w]", " ", text).split()
    bad_words = [w for w in words if w.lower() in settings.PROFANITIES_LIST]
    if bad_words:
        return True
    return False
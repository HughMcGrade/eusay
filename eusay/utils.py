from django.template.defaultfilters import slugify


def better_slugify(text, **kwargs):
            # The SlugField has a max length of 50 characters, so we make
            # sure it doesn't exceed that.
            slug = slugify(text)[:50]

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
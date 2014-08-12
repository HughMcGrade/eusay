import re
import random

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


def add_users(amount):
    """
    Add a bunch of users.
    :param amount: number of users to be added
    :return: True if successful, False otherwise
    """
    from .models import User

    names = ['Tonja','Kaley','Bo','Tobias','Jacqui','Lorena','Isaac','Adriene','Tuan','Shanon','Georgette','Chas','Yuonne','Michelina','Juliana','Odell','Juliet','Carli','Asha','Pearl','Kamala','Rubie','Elmer','Taren','Salley','Raymonde','Shelba','Alison','Wilburn','Katy','Denyse','Rosemary','Brooke','Carson','Tashina','Kristi','Aline','Yevette','Eden','Christoper','Juana','Marcie','Wendell','Vonda','Dania','Sheron','Meta','Frank','Thad','Cherise']
    generate_name = lambda: names[round((random.random() * 100) % 50) - 1]

    def increment_sid():
        last_user = User.objects.latest("createdAt")
        last_sid_num = int(last_user.sid[1:])
        new_sid_num = last_sid_num + 1
        new_sid = "s{}".format(str(new_sid_num))
        return new_sid

    # If no users exist, add one
    if User.objects.all().count() == 0:
        User.objects.get_or_create(sid="s1",
                                   name=(generate_name() + "1"))
        amount -= 1

    start_num = User.objects.all().count() + 1

    i = start_num
    while i <= start_num + amount:
        name = generate_name() + str(i)
        sid = increment_sid()
        if not User.objects.filter(sid=sid).exists():
            User.objects.create(sid=sid,
                                name=name)
            i += 1

    return True


def add_proposals(amount):
    """
    Add a bunch of (very!) generic proposals
    :param amount: number of proposals to be added
    :return: True if successful, False otherwise
    """

    from .models import Proposal, User
    titles = [
        "Praesent commodo. Cursus magna, vel scelerisque!",
        "Donec ullamcorper nulla non metus auctor fringilla!",
        "Maecenas sed diam eget risus varius blandit non magna.",
        "Etiam porta sem malesuada magna mollis euismod.",
        "Cras mattis consectetur purus sit amet fermentum!",
        "Praesent commodo cursus magna, vel scelerisque et.",
        "Maecenas sed diam eget risus varius non magna.",
        "Integer posuere erat a ante venenatis dapibus."
        "Ipsum Etiam Justo Lorem Ultricies",
        "Ridiculus Fringilla",
        "Ornare Fusce Euismod!"
    ]

    bodies = [
        "Duis mollis, est non commodo luctus, nisi erat porttitor ligula, eget lacinia odio sem nec elit. Etiam porta sem malesuada magna mollis euismod. Vestibulum id ligula porta felis euismod semper. Etiam porta sem malesuada magna mollis euismod. Cras mattis consectetur purus sit amet fermentum. Cras justo odio, dapibus ac facilisis in, egestas eget quam.",
        "Cras mattis consectetur purus sit amet fermentum. Aenean eu leo quam. Pellentesque ornare sem lacinia quam venenatis vestibulum. Duis mollis, est non commodo luctus, nisi erat porttitor ligula, eget lacinia odio sem nec elit. Nullam quis risus eget urna mollis ornare vel eu leo. Cras justo odio, dapibus ac facilisis in, egestas eget quam. Cras mattis consectetur purus sit amet fermentum. Donec sed odio dui.",
        "Etiam porta sem malesuada magna mollis euismod. Morbi leo risus, porta ac consectetur ac, vestibulum at eros. Nulla vitae elit libero, a pharetra augue. Aenean eu leo quam. Pellentesque ornare sem lacinia quam venenatis vestibulum. Nullam id dolor id nibh ultricies vehicula ut id elit. Donec id elit non mi porta gravida at eget metus. Donec sed odio dui."
    ]

    get_title = lambda: random.choice(titles)
    get_body = lambda: random.choice(bodies)

    # If no users exist, add one
    if User.objects.all().count() == 0:
        add_users(1)

    start_num = Proposal.objects.all().count() + 1

    for i in range(start_num, start_num + amount + 1):
        user = random.choice(User.objects.all())
        Proposal.objects.create(title=get_title(),
                                text=get_body(),
                                user=user)
    return True


def add_comments(amount):
    """
    Add a bunch of top-level and reply comments to the latest proposal
    :param amount: number of comments to be added
    :param proposal_id: proposal to add comments to
    :return: True if successful, False otherwise
    """
    from .models import Proposal, User, Comment
    comments = [
        "Praesent commodo. Cursus magna, vel scelerisque!",
        "Donec ullamcorper nulla non metus auctor fringilla!",
        "Maecenas sed diam eget risus varius blandit non magna.",
        "Etiam porta sem malesuada magna mollis euismod.",
        "Cras mattis consectetur purus sit amet fermentum!",
        "Praesent commodo cursus magna, vel scelerisque et.",
        "Maecenas sed diam eget risus varius non magna.",
        "Integer posuere erat a ante venenatis dapibus."
        "Ipsum Etiam Justo Lorem Ultricies",
        "Ridiculus Fringilla",
        "Ornare Fusce Euismod!"
    ]

    proposal = Proposal.objects.latest("createdAt")

    for i in range(amount + 1):
        user = random.choice(User.objects.all())
        top_level_comments = Comment.objects.filter(proposal=proposal,
                                                    replyTo=None)
        if random.random() > 0.5 and top_level_comments.count() > 0:
            reply_to = random.choice(Comment.objects.filter(proposal=proposal))
            Comment.objects.create(text=random.choice(comments),
                                   user=user,
                                   proposal=proposal,
                                   replyTo=reply_to)
        else:
            Comment.objects.create(text=random.choice(comments),
                                   user=user,
                                   proposal=proposal)

    return True


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
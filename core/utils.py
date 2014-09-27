"""Core utilities including swear check and testing utilities"""

import re
import random
from collections import OrderedDict

from django.conf import settings
from django.contrib.auth import get_user_model


def smart_truncate(content, max_length=100, suffix='...'):
    # Thanks to http://stackoverflow.com/questions/250357/
    if len(content) <= max_length:
        return content
    else:
        return content[:max_length].rsplit(' ', 1)[0]+suffix


def add_users(amount):
    """
    Add a bunch of users.

    :param amount: Number of users to be added
    :return:       True if successful, False otherwise
    """

    names = ['Tonja', 'Kaley', 'Bo', 'Tobias', 'Jacqui', 'Lorena', 'Isaac',
             'Adriene', 'Tuan', 'Shanon', 'Georgette', 'Chas', 'Yuonne',
             'Michelina', 'Juliana', 'Odell', 'Juliet', 'Carli', 'Asha',
             'Pearl', 'Kamala', 'Rubie', 'Elmer', 'Taren', 'Salley',
             'Raymonde', 'Shelba', 'Alison', 'Wilburn', 'Katy', 'Denyse',
             'Rosemary', 'Brooke', 'Carson', 'Tashina', 'Kristi', 'Aline',
             'Yevette', 'Eden', 'Christoper', 'Juana', 'Marcie', 'Wendell',
             'Vonda', 'Dania', 'Sheron', 'Meta', 'Frank', 'Thad', 'Cherise']
    generate_name = lambda: random.choice(names)

    def increment_sid():
        last_user = get_user_model().objects.latest("date_joined")
        last_sid_num = int(last_user.sid[1:])
        new_sid_num = last_sid_num + 1
        new_sid = "s{}".format(str(new_sid_num))
        return new_sid

    # If no users exist, add one
    if get_user_model().objects.all().count() == 0:
        get_user_model().objects.get_or_create(sid="s1",
                                               username=(generate_name()
                                                         + "1"))
        amount -= 1

    start_num = get_user_model().objects.all().count() + 1

    i = start_num
    while i <= start_num + amount:
        name = generate_name() + str(i)
        sid = increment_sid()
        if not get_user_model().objects.filter(sid=sid).exists():
            get_user_model().objects.create(sid=sid,
                                            username=name)
            i += 1

    return True


def add_proposals(amount):
    """
    Add a bunch of (very!) generic proposals

    :param amount: Number of proposals to be added
    :return:       True if successful, False otherwise
    """

    from proposals.models import Proposal
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
        "Duis mollis, est non commodo luctus, nisi "
        "erat porttitor ligula, eget lacinia odio sem "
        "nec elit. Etiam porta sem malesuada magna mollis euismod. "
        "Vestibulum id ligula porta felis euismod semper. Etiam porta sem "
        "malesuada magna mollis euismod. Cras mattis consectetur purus sit "
        "amet fermentum. Cras justo odio, dapibus ac facilisis in, egestas "
        "eget quam.",

        "Cras mattis consectetur purus sit amet fermentum. Aenean eu leo "
        "quam. Pellentesque ornare sem lacinia quam venenatis vestibulum. "
        "Duis mollis, est non commodo luctus, nisi erat porttitor ligula, "
        "eget lacinia odio sem nec elit. Nullam quis risus eget urna mollis "
        "ornare vel eu leo. Cras justo odio, dapibus ac facilisis in, egestas "
        "eget quam. Cras mattis consectetur purus sit amet fermentum. Donec "
        "sed odio dui.",

        "Etiam porta sem malesuada magna mollis euismod. Morbi leo risus, "
        "porta ac consectetur ac, vestibulum at eros. Nulla vitae elit "
        "libero, a pharetra augue. Aenean eu leo quam. Pellentesque ornare "
        "sem lacinia quam venenatis vestibulum. Nullam id dolor id nibh "
        "ultricies vehicula ut id elit. Donec id elit non mi porta gravida "
        "at eget metus. Donec sed odio dui."
    ]

    get_title = lambda: random.choice(titles)
    get_body = lambda: random.choice(bodies)

    from tags.models import Tag
    get_tags = lambda: Tag.objects.all().order_by('?')[:3]

    # If no users exist, add one
    if get_user_model().objects.all().count() == 0:
        add_users(1)

    start_num = Proposal.objects.all().count() + 1

    for i in range(start_num, start_num + amount + 1):
        user = random.choice(get_user_model().objects.all())
        proposal = Proposal.objects.create(title=get_title(),
                                text=get_body(),
                                user=user)
        for tag in get_tags():
            proposal.tags.add(tag)
        proposal.save()
    return True


def add_comments(amount):
    """
    Add a bunch of top-level and reply comments to the latest proposal

    :param amount:      Number of comments to be added
    :param proposal_id: Proposal to add comments to
    :return:            True if successful, False otherwise
    """
    from proposals.models import Proposal
    from comments.models import Comment
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
        user = random.choice(get_user_model().objects.all())
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


def add_tags():
    from tags.models import Tag
    from django.db.utils import IntegrityError
    tags = ['School of Informatics', 'School of Biological Sciences',
            'School of Biomedical Sciences', 'Business School',
            'School of Chemistry', 'School of Clinical Sciences',
            'School of Divinity', 'School of Economics',
            'Edinburgh College of Art', 'The Moray House School of Education',
            'School of Engineering', 'School of GeoSciences',
            'School of Health in Social Science',
            'School of History, Classics and Archaeology', 'School of Law',
            'School of Literatures, Languages and Cultures',
            'School of Mathematics',
            # Below broken, see stackoverflow.com/questions/9036102/
            # 'School of Molecular, Genetic and Population Health Sciences'
            # 'School of Philosophy, Psychology and Language Sciences'
            'School of Physics and Astronomy',
            'School of Social and Political Science',
            'Royal (Dick) School of Veterinary Studies']
    for tag in tags:
        try:
            Tag.objects.create(name=tag)
        except IntegrityError as error:
            print(error)


def to_queryset(searchqueryset):
    """
    This function converts a SearchQuerySet into a QuerySet.

    We don't use a generator here because pagination in the API requires
    that you can take the len() of a list, a generators don't have a len().
    """
    return [item.object for item in searchqueryset]


def contains_swear_words(text):
    words = re.sub(r"[^\w]", " ", text).split()
    bad_words = [w for w in words if w.lower() in settings.PROFANITIES_LIST]
    return bool(bad_words)


def sqs_to_qs(sqs):
    for item in sqs:
        yield item.object


def is_sid(value):
    sid = re.compile(r"^s\d{7}$")
    return sid.match(value)


def remove_duplicates(seq):
    return list(OrderedDict.fromkeys(seq))
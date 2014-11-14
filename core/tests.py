"""Currently no tests for Core"""
from django.test import TestCase

from proposals.models import Proposal
from users.models import User
from tags.models import Tag
from moderation.models import HideAction, Report
from comments.models import Comment
import haystack
from django.test.utils import override_settings
from django.core.management import call_command
import os


TEST_INDEX = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'test_index'),
    },
}


def add_objects(self):
    """
    Add test objects to test database.
    """
    self.user = User.objects.create_user(sid="s1234567", userStatus="User",
                                         username="Urquell", hasProfile=True,
                                         password="")
    self.eusa_staff = User.objects.create_user(sid="12345", userStatus="Staff",
                                               username="Frances",
                                               isModerator=True, password="")
    self.candidate = User.objects.create_user(sid="s7654321",
                                              userStatus="Candidate",
                                              username="Tony", password="")
    self.officeholder = User.objects.create_user(sid="s3214321",
                                                 userStatus="Officeholder",
                                                 username="Nicola",
                                                 password="")
    self.tag = Tag.objects.create(name="Fun", description="FUN FUN FUN", group=1)
    self.proposal = Proposal.objects.create(title="Cascada and Venga"
                                            "Boys at Potterow all year.",
                                            text="EUSA shall book Cascada "
                                            "and Venga Boys alternating on "
                                            "weekends throughout the whole "
                                            "year. Additional costs shall be "
                                            "paid by the University's "
                                            "principal. In return, the "
                                            "principal is granted compulsory "
                                            "free entry till 11pm and drink "
                                            "vouchers worth \u00a337.85. This "
                                            "new event structure would "
                                            "provide the University community "
                                            "with the opportunity to party "
                                            "with its principal every "
                                            "Saturday to classics like "
                                            "\"Every time we "
                                            "touch\" or \"Boom, boom, boom, "
                                            "boom, I want you in my room\".",
                                            user=self.user)
    self.proposal.tags.add(self.tag)
    self.comment = Comment.objects.create(text="What about the Chancellor?",
                                          proposal=self.proposal,
                                          user=self.user)
    self.reply = Comment.objects.create(text="John, get the heck outta here",
                                        proposal=self.proposal,
                                        user=self.officeholder,
                                        replyTo=self.comment)
    self.hidden_proposal = Proposal.objects.create(title="Do very bad and "
                                                         "offensive things",
                                                   text="I think EUSA should "
                                                        "do things which are "
                                                        "not safe space "
                                                        "at all",
                                                   user=self.candidate)
    self.proposal_hide = HideAction.objects.create(moderator=self.eusa_staff,
                                                   reason="Bad and offensive "
                                                          "things are not "
                                                          "safe space",
                                                   content=self.
                                                   hidden_proposal)
    self.hidden_comment = Comment.objects.create(text="Something offensive",
                                                 proposal=self.proposal,
                                                 user=self.user)
    self.comment_hide = HideAction.objects.create(moderator=self.eusa_staff,
                                                  reason="This offensive "
                                                         "content is not "
                                                         "acceptable on eusay",
                                                  content=self.hidden_comment)
    self.reported_comment = Comment.objects.create(proposal=self.proposal,
                                                   text="Possibly not safe "
                                                        "space",
                                                   user=self.candidate)
    self.comment_report = Report.objects.create(content=self.reported_comment,
                                                reason="Offensive",
                                                reporter=self.user)
    self.reported_proposal = Proposal.objects.create(title="Do things some "
                                                     "may find offensive",
                                                     text="I think EUSA "
                                                          "should do things "
                                                          "which some "
                                                          "people may find "
                                                          "offensive.",
                                                     user=self.candidate)
    self.proposal_report = Report.objects.create(
        content=self.reported_proposal,
        reason="Daft",
        reporter=self.user)


@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class BaseTestCase(TestCase):
    """
    Base class for all test cases setting up Haystack and adding objects.
    """
    def setUp(self):
        add_objects(self)
        haystack.connections.reload('default')
        super(BaseTestCase, self).setUp()

    def tearDown(self):
        call_command('clear_index', interactive=False, verbosity=0)

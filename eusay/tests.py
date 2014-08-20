from django.test import TestCase
from django.core.urlresolvers import reverse

from eusay import models

def addObjects(self):
    self.user = models.User.objects.create_user(sid="s1234567", userStatus="User", username="Urquell", hasProfile=True, password="")
    self.eusa_staff = models.User.objects.create_user(sid="12345", userStatus="Staff", username="Frances", isModerator=True, password="")
    self.candidate = models.User.objects.create_user(sid="s7654321", userStatus="Candidate", username="Tony", password="")
    self.officeholder = models.User.objects.create_user(sid="s3214321", userStatus="Officeholder", username="Nicola", password="")
    self.tag = models.Tag.objects.create(name="Fun", description="FUN FUN FUN")
    self.proposal = models.Proposal.objects.create(title="Cascada and Venga Boys at Potterow all year.", text="EUSA shall book Cascada and Venga Boys alternating on weekends throughout the whole year. Additional costs shall be paid by the University's principal. In return, the principal is granted compulsory free entry till 11pm and drink vouchers worth \u00a337.85. This new event structure would provide the University community with the opportunity to party with its principal every Saturday to classics like \"Every time we touch\" or \"Boom, boom, boom, boom, I want you in my room\".", user=self.user)
    self.proposal.tags.add(self.tag)
    self.comment = models.Comment.objects.create(text="What about the Chancellor?", proposal=self.proposal, user=self.user)
    self.reply = models.Comment.objects.create(text="John, get the heck outta here", proposal=self.proposal, user=self.officeholder, replyTo=self.comment)
    self.hidden_proposal = models.Proposal.objects.create(title="Do very bad and offensive things", text="I think EUSA should do things which are not safe space at all", user=self.candidate)
    self.proposal_hide = models.HideAction.objects.create(moderator=self.eusa_staff, reason="Bad and offensive things are not safe space", content=self.hidden_proposal)
    self.hidden_comment = models.Comment.objects.create(text="Something offensive", proposal=self.proposal, user=self.user)
    self.comment_hide = models.HideAction.objects.create(moderator=self.eusa_staff, reason="This offensive content is not acceptable on eusay", content=self.hidden_comment)
    self.reported_comment = models.Comment.objects.create(proposal=self.proposal, text="Possibly not safe space", user=self.candidate)
    self.comment_report = models.Report.objects.create(content=self.reported_comment, reason="Offensive", reporter=self.user)
    self.reported_proposal = models.Proposal.objects.create(title="Do things some may find offensive", text="I think EUSA should do things which some people may find offensive.", user=self.candidate)
    self.proposal_report = models.Report.objects.create(content=self.reported_proposal, reason="Daft", reporter=self.user)


class TestSearch (TestCase):
    # TODO
    pass

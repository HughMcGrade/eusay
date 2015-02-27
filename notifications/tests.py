from django.core.urlresolvers import reverse

from comments.models import Comment
from core.tests import BaseTestCase
from proposals.models import Proposal, Response
from votes.models import Vote

class ProposalNotificationsTest(BaseTestCase):

    def clearNotifications(self):
        for n in self.user.notifications.all():
            n.mark_as_read()
            n.save()

    def assertHasNotificationOfType(self, type):
        self.client.login(username=self.user.username,
                          password="")
        response = self.client.get(reverse('notifications:all'))
        self.assertEqual(response.status_code, 200)
        notifications = response.context['unread']
        self.assertEqual(len(notifications), 1)
        self.assertEqual(list(notifications)[0][0][0], type)

    def testNewProposal(self):
        self.clearNotifications()
        self.user.follows_tags.add(self.tag)
        proposal = Proposal.objects.create(
            user=self.eusa_staff,
            title='Call \'WiFi\' \'WLAN\'',
            text='I think WLAN is a better name')
        proposal.tags.add(self.tag)
        self.assertHasNotificationOfType("new_proposal")

    def testNotifyOfResponse(self):
        self.clearNotifications()
        Response.objects.create(
            text="This is a great idea",
            user=self.eusa_staff,
            proposal=self.proposal)
        self.assertHasNotificationOfType("proposal_response")
        
    def testNotifyProposerOfComment(self):
        self.clearNotifications()
        Comment.objects.create(
            proposal=self.proposal,
            text="Good idea",
            user=self.eusa_staff
        )
        self.assertHasNotificationOfType("proposal_comment")

    def testNotifyProposerOfAmendment(self):
        self.clearNotifications()
        Comment.objects.create(
            proposal=self.proposal,
            text="Completely new text!",
            user=self.eusa_staff,
            isAmendment=True
        )
        self.assertHasNotificationOfType("proposal_amendment")

    # Tests both reply and reply in thread
    def testNotifyCommenterOfReplies(self):
        self.clearNotifications()
        proposal = Proposal.objects.create(
            title="Another proposal.",
            text="Just another proposal",
            user=self.eusa_staff)
        comment = Comment.objects.create(
            proposal=self.proposal,
            text="A provocative comment",
            user=self.user)
        Comment.objects.create(
            proposal=proposal,
            replyTo=comment,
            user=self.eusa_staff)
        self.assertHasNotificationOfType("comment_reply")
        self.clearNotifications()
        Comment.objects.create(
            proposal=proposal,
            replyTo=comment,
            user=self.eusa_staff)
        self.assertHasNotificationOfType("comment_reply")

    def testNotifyOfVote(self):
        self.clearNotifications()
        Vote.objects.create(
            content=self.proposal,
            isVoteUp=True,
            user=self.eusa_staff)
        self.assertHasNotificationOfType("proposal_vote_up")
        self.clearNotifications()
        Vote.objects.create(
            content=self.proposal,
            isVoteUp=False,
            user=self.eusa_staff)
        self.assertHasNotificationOfType("proposal_vote_down")
        self.clearNotifications()
        Vote.objects.create(
            content=self.comment,
            isVoteUp=True,
            user=self.eusa_staff)
        self.assertHasNotificationOfType("comment_vote_up")
        self.clearNotifications()
        Vote.objects.create(
            content=self.comment,
            isVoteUp=False,
            user=self.eusa_staff)
        self.assertHasNotificationOfType("comment_vote_down")

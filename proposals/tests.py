from django.core.urlresolvers import reverse

from comments.models import Comment
from core.tests import BaseTestCase
from proposals.models import Proposal, Response


class IndexTest(BaseTestCase):

    def testViewIndex(self):
        url = reverse('frontpage')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposals', response.context)
        self.assertIn(self.proposal, response.context['proposals'])


class ProposalTest(BaseTestCase):

    def testSubmit(self):
        # Test load submit page anonymously
        url = reverse('submit')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Test submit proposal anonymously
        title = 'Call \'WiFi\' \'WLAN\''
        text = 'I think WLAN is a better name'
        post = {'title': title, 'text': text}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)

        # Log in
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=""))

        # Load submit page
        url = reverse('submit')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Submit proposal
        title = 'Call \'WiFi\' \'WLAN\''
        text = 'I think WLAN is a better name'
        post = {'title': title, 'text': text}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Proposal.objects.get(title=title, text=text,
                                             user=self.user))

    def testView(self):
        url = reverse('proposal', kwargs={"proposal_id": self.proposal.id,
                                           "slug": self.proposal.slug})

        # View proposal anonymously
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposal', response.context)
        self.assertEqual(response.context['proposal'], self.proposal)

        # Log in
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=""))

        # View proposal (as user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposal', response.context)
        self.assertEqual(response.context['proposal'], self.proposal)

        # View hidden proposal
        url = reverse('proposal', args=[self.hidden_proposal.id,
                                        self.hidden_proposal.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('hide', response.context)
        self.assertEqual(response.context['hide'], self.proposal_hide)

    def testDeleteProposal(self):
        url = reverse('delete_proposal', args=[self.proposal.id])

        # Log in as user other than original poster
        self.assertTrue(self.client.login(username=self.officeholder.username,
                                          password=''))

        # Delete as user other than original poster
        post = {'action': 'delete'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        proposal = Proposal.objects.get(id=self.proposal.id)
        self.assertNotEqual(proposal.title, "Deleted proposal")
        self.assertNotEqual(proposal.text,
                            "This proposal has been deleted by its proposer.")

        # Log in as original poster
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=''))

        # Delete as user other than original poster
        post = {'action': 'delete'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        proposal = Proposal.objects.get(id=self.proposal.id)
        self.assertEqual(proposal.title, "Deleted proposal")
        self.assertEqual(proposal.text,
                         "This proposal has been deleted by its proposer.")


class AmendTest(BaseTestCase):

    def testAmendProposal(self):
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=''))
        url = reverse('amend_proposal', args=[self.proposal.id])
        post = {'title': 'Completely New Title',
                'text':
                'I have decided to change this proposal entirely, '
                'so it now says nothing.',
                'action': 'view'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 200)
        self.assertIn('diff', response.context)
        text = response.context['diff']
        post = {'text': text, 'action': 'post'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.get(isAmendment=True))


class ResponseTest(BaseTestCase):

    def testRespond(self):
        url = reverse('respond', args=[self.proposal.id, self.proposal.slug])

        # Respond anonymously
        post = {'text': 'My response'}
        response = self.client.get(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertRaises(Response.DoesNotExist, Response.objects.get,
                          proposal=self.proposal.id)

        # Log in as regular user
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=''))

        # View page as regular user
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Respond as regular user
        post = {'text': 'My response', 'status': Proposal.PROPOSAL_STATUS_CHOICES[1][0]}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertRaises(Response.DoesNotExist, Response.objects.get,
                          proposal=self.proposal.id)
        proposal = Proposal.objects.get(id=self.proposal.id)
        self.assertEqual(proposal.status, self.proposal.status)

        # Log in as officeholder
        self.assertTrue(self.client.login(username=self.officeholder.username,
                                          password=''))

        # View page as regular user
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Respond and update status as officeholder
        post = {'text': 'My response', 'status': Proposal.PROPOSAL_STATUS_CHOICES[1][0]}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        proposal_response = Response.objects.get(proposal=self.proposal.id)
        self.assertTrue(Response.objects.get(proposal=self.proposal.id))
        self.proposal = Proposal.objects.get(id=self.proposal.id)
        self.assertEqual(self.proposal.status, Proposal.PROPOSAL_STATUS_CHOICES[1][0])

        # View new response
        url = reverse('proposal', kwargs={"proposal_id": self.proposal.id,
                                           "slug": self.proposal.slug})
        response = self.client.get(url)
        self.assertIn('proposal', response.context)
        self.assertIn(proposal_response,
                      response.context['proposal'].responses.all())


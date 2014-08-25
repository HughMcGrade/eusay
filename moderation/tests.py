from django.test import TestCase
from django.core.urlresolvers import reverse

from core.tests import addObjects
from comments.models import Comment
from proposals.models import Proposal
from moderation.models import Report, HideAction

class HideTest (TestCase):

    def setUp(self):
        addObjects(self)

    def testHideComment(self):
        url = reverse('hide_comment', args=[self.comment.id])

        # View form anonymously
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Submit hide anonymously
        post = {'reason' : 'I want to hide'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.comment = Comment.objects.get(id=self.comment.id)
        self.assertFalse(self.comment.isHidden)

        # Log in as non-moderator
        self.assertTrue(self.client.login(username=self.user.username, password=""))

        # View form as non-moderator
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Submit hide as non-moderator
        post = {'reason' : 'I want to hide'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.comment = Comment.objects.get(id=self.comment.id)
        self.assertFalse(self.comment.isHidden)

        # Log in as moderator
        self.client.login(username=self.eusa_staff.username, password="")

        # View form as moderator
        url = reverse('hide_comment', args=[self.comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('comment', response.context)
        self.assertEqual(response.context['comment'], self.comment)

        # Submit hide as moderator
        post = {'reason' : 'I want to hide'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.comment = Comment.objects.get(id=self.comment.id)
        self.assertTrue(self.comment.isHidden)

    def testHideProposal(self):
        url = reverse('hide_proposal', args=[self.proposal.id])

        # View form anonymously
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Submit hide anonymously
        post = {'reason' : 'I want to hide'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.proposal = Proposal.objects.get(id=self.proposal.id)
        self.assertFalse(self.proposal.isHidden)

        # Log in as non-moderator
        self.assertTrue(self.client.login(username=self.user.username, password=""))

        # View form as non-moderator
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Submit hide as non-moderator
        post = {'reason' : 'I want to hide'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.proposal = Proposal.objects.get(id=self.proposal.id)
        self.assertFalse(self.proposal.isHidden)

        # Log in as moderator
        self.client.login(username=self.eusa_staff.username, password="")

        # View form as moderator
        url = reverse('hide_proposal', args=[self.proposal.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('proposal', response.context)
        self.assertEqual(response.context['proposal'], self.proposal)

        # Submit hide as moderator
        post = {'reason' : 'I want to hide'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.proposal = Proposal.objects.get(id=self.proposal.id)
        self.assertTrue(self.proposal.isHidden)

    def testViewHiddenComments(self):
        url = reverse('hidden_comments')
        response = self.client.get(url)
        self.assertIn('hiddens', response.context)
        self.assertIn(self.comment_hide, response.context['hiddens'])

    def testViewHiddenProposals(self):
        url = reverse('hidden_proposals')
        response = self.client.get(url)
        self.assertIn('hiddens', response.context)
        self.assertIn(self.proposal_hide, response.context['hiddens'])

class ReportTest (TestCase):

    def setUp(self):
        addObjects(self)

    def testReportComment(self):
        # View form anonymously
        url = reverse('report_comment', args=[self.comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Report anonymously
        post = {'reason' : 'Unacceptable'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Report.objects.filter(content_type=Comment.get_content_type(), object_id=self.comment.id))

        # Log in
        self.client.login(username=self.eusa_staff.username, password="")
        
        # View form
        url = reverse('report_comment', args=[self.comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('comment', response.context)
        self.assertEqual(self.comment, response.context['comment'])

        # Report
        post = {'reason' : 'Unacceptable'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Report.objects.filter(content_type=Comment.get_content_type(), object_id=self.comment.id))

    def testReportProposal(self):
        # View form anonymously
        url = reverse('report_proposal', args=[self.proposal.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Report anonymously
        post = {'reason' : 'Unacceptable'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Report.objects.filter(content_type=Proposal.get_content_type(), object_id=self.proposal.id))

        # Log in
        self.client.login(username=self.eusa_staff.username, password="")
        
        # View form
        url = reverse('report_proposal', args=[self.proposal.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('proposal', response.context)
        self.assertEqual(self.proposal, response.context['proposal'])

        # Report
        post = {'reason' : 'Unacceptable'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Report.objects.filter(content_type=Proposal.get_content_type(), object_id=self.proposal.id))

    def testModeratorPanel(self):
        url = reverse('moderator_panel')

        # View moderator panel anonymously
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # Hide from comment report anonymously
        post = {'action' : 'Hide', 'report' : self.comment_report.id}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertRaises(HideAction.DoesNotExist, HideAction.objects.get, object_id=self.reported_comment.id, content_type=Comment.get_content_type())
        self.assertTrue(Report.objects.get(id=self.comment_report.id))

        # Hide from proposal report anonymously
        post = {'action' : 'Hide', 'report' : self.proposal_report.id}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertRaises(HideAction.DoesNotExist, HideAction.objects.get, object_id=self.reported_proposal.id, content_type=Proposal.get_content_type())
        self.assertTrue(Report.objects.get(id=self.proposal_report.id))

        # Login as non-moderator
        self.assertTrue(self.client.login(username=self.user.username, password=''))

        # View moderator panel as non-moderator
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # Hide from comment report as non-moderator
        post = {'action' : 'Hide', 'report' : self.comment_report.id}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertRaises(HideAction.DoesNotExist, HideAction.objects.get, object_id=self.reported_comment.id, content_type=Comment.get_content_type())
        self.assertTrue(Report.objects.get(id=self.comment_report.id))

        # Hide from proposal report as non-moderator
        post = {'action' : 'Hide', 'report' : self.proposal_report.id}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertRaises(HideAction.DoesNotExist, HideAction.objects.get, object_id=self.reported_proposal.id, content_type=Proposal.get_content_type())
        self.assertTrue(Report.objects.get(id=self.proposal_report.id))

        # Login as moderator
        self.assertTrue(self.client.login(username=self.eusa_staff.username, password=''))

        # View moderator panel as moderator
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Hide from comment report as moderator
        post = {'action' : 'Hide', 'report' : self.comment_report.id}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(HideAction.objects.get(object_id=self.reported_comment.id, content_type=Comment.get_content_type()))
        self.assertRaises(Report.DoesNotExist, Report.objects.get, id=self.comment_report.id)

        # Hide from proposal report as moderator
        post = {'action' : 'Hide', 'report' : self.proposal_report.id}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(HideAction.objects.get(object_id=self.reported_proposal.id, content_type=Proposal.get_content_type()))
        self.assertRaises(Report.DoesNotExist, Report.objects.get, id=self.proposal_report.id)

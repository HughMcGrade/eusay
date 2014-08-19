from django.test import TestCase
from eusay.models import *
from eusay.forms import *
from eusay.views import *

def addObjects(self):
    self.user = User.objects.create_user(sid="s1234567", userStatus="User", username="Urquell", hasProfile=True, password="")
    self.eusa_staff = User.objects.create_user(sid="12345", userStatus="Staff", username="Frances", isModerator=True, password="")
    self.candidate = User.objects.create_user(sid="s7654321", userStatus="Candidate", username="Tony", password="")
    self.officeholder = User.objects.create_user(sid="s3214321", userStatus="Officeholder", username="Nicola", password="")
    self.tag = Tag.objects.create(name="Fun", description="FUN FUN FUN")
    self.proposal = Proposal.objects.create(title="Cascada and Venga Boys at Potterow all year.", text="EUSA shall book Cascada and Venga Boys alternating on weekends throughout the whole year. Additional costs shall be paid by the University's principal. In return, the principal is granted compulsory free entry till 11pm and drink vouchers worth \u00a337.85. This new event structure would provide the University community with the opportunity to party with its principal every Saturday to classics like \"Every time we touch\" or \"Boom, boom, boom, boom, I want you in my room\".", user=self.user)
    self.proposal.tags.add(self.tag)
    self.comment = Comment.objects.create(text="What about the Chancellor?", proposal=self.proposal, user=self.user)
    self.reply = Comment.objects.create(text="John, get the heck outta here", proposal=self.proposal, user=self.officeholder, replyTo=self.comment)
    self.hidden_proposal = Proposal.objects.create(title="Do very bad and offensive things", text="I think EUSA should do things which are not safe space at all", user=self.candidate)
    self.proposal_hide = HideAction.objects.create(moderator=self.eusa_staff, reason="Bad and offensive things are not safe space", content=self.hidden_proposal)
    self.hidden_comment = Comment.objects.create(text="Something offensive", proposal=self.proposal, user=self.user)
    self.comment_hide = HideAction.objects.create(moderator=self.eusa_staff, reason="This offensive content is not acceptable on eusay", content=self.hidden_comment)
    self.reported_comment = Comment.objects.create(proposal=self.proposal, text="Possibly not safe space", user=self.candidate)
    self.comment_report = Report.objects.create(content=self.reported_comment, reason="Offensive", reporter=self.user)
    self.reported_proposal = Proposal.objects.create(title="Do things some may find offensive", text="I think EUSA should do things which some people may find offensive.", user=self.candidate)
    self.proposal_report = Report.objects.create(content=self.reported_proposal, reason="Daft", reporter=self.user)

class IndexTest (TestCase):
    
    def setUp(self):
        addObjects(self)

    def testViewIndex(self):
        url = reverse('frontpage')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposals', response.context)
        self.assertIn(self.proposal, response.context['proposals'])

class ProposalTest (TestCase):

    def setUp(self):
        addObjects(self)
    
    def testSubmit(self):
        # Test load submit page anonymously
        url = reverse('submit')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # Test submit proposal anonymously
        title = 'Call \'WiFi\' \'WLAN\''
        text = 'I think WLAN is a better name'
        post  = {'title':title, 'text':text}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)

        # Log in
        self.assertTrue(self.client.login(username=self.user.username, password=""))

        # Load submit page
        url = reverse('submit')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Submit proposal
        title = 'Call \'WiFi\' \'WLAN\''
        text = 'I think WLAN is a better name'
        post  = {'title':title, 'text':text}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Proposal.objects.get(title=title, text=text, user=self.user))

    def testView(self):
        url = reverse('proposal', args=[self.proposal.id, self.proposal.slug])

        # View proposal anonymously
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposal', response.context)
        self.assertEqual(response.context['proposal'], self.proposal)

        # Log in
        self.assertTrue(self.client.login(username=self.user.username, password=""))

        # View proposal (as user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposal', response.context)
        self.assertEqual(response.context['proposal'], self.proposal)

        # View hidden proposal
        url = reverse('proposal', args=[self.hidden_proposal.id, self.hidden_proposal.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('hide', response.context)
        self.assertEqual(response.context['hide'], self.proposal_hide)

class TagTest (TestCase):
    
    def setUp(self):
        addObjects(self)

    def testView(self):
        url = reverse('tag', args=[self.tag.id, self.tag.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposals', response.context)
        self.assertIn(self.proposal, response.context['proposals'])
        # TODO Test sort?

class ProfileTest (TestCase):

    def setUp(self):
        addObjects(self)

    def testViewAsSelf(self):
        self.client.login(username=self.user.username, password="")
        url = reverse('user', args=[self.user.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile', response.context)
        self.assertIn('form', response.context)

    def testViewForHasProfile(self):
        url = reverse('user', args=[self.user.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile', response.context)
        self.assertNotIn('form', response.context)

    def testViewForNoProfile(self):
        url = reverse('user', args=[self.eusa_staff.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile', response.context)
        self.assertNotIn('form', response.context)

    def testChangeUsername(self):
        url = reverse('user', args=[self.user.slug])
        
        # Log in as another user
        self.client.login(username=self.eusa_staff.username, password="")

        # Change other user's username
        post = {'username' : 'Brendan', 'hasProfile' : self.user.hasProfile}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 200)
        previous_name = self.user.username
        self.user = User.objects.get(id=self.user.id)
        self.assertEqual(self.user.username, previous_name)

        # Log in as self
        self.client.login(username=self.user.username, password="")

        # Change own username
        post = {'username' : 'Brendan', 'hasProfile' : self.user.hasProfile}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.user = User.objects.get(id=self.user.id)
        self.assertEqual(self.user.username, 'Brendan')
        
    def testChangeHasProfile(self):
        url = reverse('user', args=[self.user.slug])
        
        # Log in as another user
        self.client.login(username=self.eusa_staff.username, password="")

        # Change other user's hasProfile value
        post = {'username':self.user.username, 'hasProfile' : not self.user.hasProfile}
        response = self.client.post(url, post)
        previous_value = self.user.hasProfile
        self.user = User.objects.get(id=self.user.id)
        self.assertEqual(self.user.hasProfile, previous_value)

        # Log in as self
        self.client.login(username=self.user.username, password="")

        # Change own hasProfile value
        post = {'username':'Brendan', 'hasProfile' : not self.user.hasProfile}
        response = self.client.post(url, post)
        previous_value = self.user.hasProfile
        self.user = User.objects.get(id=self.user.id)
        self.assertEqual(self.user.hasProfile, not previous_value)

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
        self.assertTrue(Report.objects.filter(content_type=Comment.contentType(), object_id=self.comment.id))

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
        self.assertTrue(Report.objects.filter(content_type=Comment.contentType(), object_id=self.comment.id))

    def testReportProposal(self):
        # View form anonymously
        url = reverse('report_proposal', args=[self.proposal.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Report anonymously
        post = {'reason' : 'Unacceptable'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Report.objects.filter(content_type=Proposal.contentType(), object_id=self.proposal.id))

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
        self.assertTrue(Report.objects.filter(content_type=Proposal.contentType(), object_id=self.proposal.id))

    def testModeratorPanel(self):
        url = reverse('moderator_panel')

        # View moderator panel anonymously
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # Hide from comment report anonymously
        post = {'action' : 'Hide', 'report' : self.comment_report.id}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertRaises(HideAction.DoesNotExist, HideAction.objects.get, object_id=self.reported_comment.id, content_type=Comment.contentType())
        self.assertTrue(Report.objects.get(id=self.comment_report.id))

        # Hide from proposal report anonymously
        post = {'action' : 'Hide', 'report' : self.proposal_report.id}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertRaises(HideAction.DoesNotExist, HideAction.objects.get, object_id=self.reported_proposal.id, content_type=Proposal.contentType())
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
        self.assertRaises(HideAction.DoesNotExist, HideAction.objects.get, object_id=self.reported_comment.id, content_type=Comment.contentType())
        self.assertTrue(Report.objects.get(id=self.comment_report.id))

        # Hide from proposal report as non-moderator
        post = {'action' : 'Hide', 'report' : self.proposal_report.id}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertRaises(HideAction.DoesNotExist, HideAction.objects.get, object_id=self.reported_proposal.id, content_type=Proposal.contentType())
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
        self.assertTrue(HideAction.objects.get(object_id=self.reported_comment.id, content_type=Comment.contentType()))
        self.assertRaises(Report.DoesNotExist, Report.objects.get, id=self.comment_report.id)

        # Hide from proposal report as moderator
        post = {'action' : 'Hide', 'report' : self.proposal_report.id}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(HideAction.objects.get(object_id=self.reported_proposal.id, content_type=Proposal.contentType()))
        self.assertRaises(Report.DoesNotExist, Report.objects.get, id=self.proposal_report.id)

class ResponseTest (TestCase):

    def setUp(self):
        addObjects(self)

    def testRespond(self):
        url = reverse('respond', args=[self.proposal.id, self.proposal.slug])

        # Respond anonymously
        post = {'text' : 'My response'}
        response = self.client.get(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertRaises(Response.DoesNotExist, Response.objects.get, proposal=self.proposal.id)

        # Log in as regular user
        self.assertTrue(self.client.login(username=self.user.username, password=''))

        # View page as regular user
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Respond as regular user
        post = {'text' : 'My response'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertRaises(Response.DoesNotExist, Response.objects.get, proposal=self.proposal.id)

        # Log in as officeholder
        self.assertTrue(self.client.login(username=self.officeholder.username, password=''))

        # View page as regular user
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Respond as officeholder
        post = {'text' : 'My response'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        proposal_response = Response.objects.get(proposal=self.proposal.id)
        self.assertTrue(Response.objects.get(proposal=self.proposal.id))
        
        # View new response
        url = reverse('proposal', args=[self.proposal.id, self.proposal.slug])
        response = self.client.get(url)
        self.assertIn('proposal', response.context)
        self.assertEqual(response.context['proposal'].response, proposal_response)

class DeleteTest (TestCase):

    def setUp(self):
        addObjects(self)

    def testDeleteComment(self):
        url = reverse('delete_comment', args=[self.comment.id])
        
        # Log in as user other than original poster
        self.assertTrue(self.client.login(username=self.officeholder.username, password=''))

        # View page as user other than original poster
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Delete as user other than original poster
        post = {'action' : 'delete'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(id=self.comment.id)
        self.assertNotEqual(comment.text, "This comment has been deleted by its creator.")

        # Log in as original poster
        self.assertTrue(self.client.login(username=self.user.username, password=''))

        # View page as original poster
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Delete as user other than original poster
        post = {'action' : 'delete'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.comment = Comment.objects.get(id=self.comment.id)
        self.assertEqual(self.comment.text, "This comment has been deleted by its creator.")

    def testDeleteProposal(self):
        url = reverse('delete_proposal', args=[self.proposal.id])
        
        # Log in as user other than original poster
        self.assertTrue(self.client.login(username=self.officeholder.username, password=''))

        # Delete as user other than original poster
        post = {'action' : 'delete'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        proposal = Proposal.objects.get(id=self.proposal.id)
        self.assertNotEqual(proposal.title, "Deleted proposal")
        self.assertNotEqual(proposal.text, "This proposal has been deleted by its proposer.")

        # Log in as original poster
        self.assertTrue(self.client.login(username=self.user.username, password=''))

        # Delete as user other than original poster
        post = {'action' : 'delete'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        proposal = Proposal.objects.get(id=self.proposal.id)
        self.assertEqual(proposal.title, "Deleted proposal")
        self.assertEqual(proposal.text, "This proposal has been deleted by its proposer.")

class AmendTest (TestCase):

    def setUp(self):
        addObjects(self)

    def testAmendProposal(self):
        self.assertTrue(self.client.login(username=self.user.username, password=''))
        url = reverse('amend_proposal', args=[self.proposal.id])
        post = {'title':'Completely New Title', 'text':'I have decided to change this proposal entirely, so it now says nothing.', 'action' : 'view'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 200)
        self.assertIn('diff', response.context)
        text = response.context['diff']
        post = {'text' : text, 'action' : 'post'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.get(isAmendment=True))

class TestSearch (TestCase):
    # TODO
    pass

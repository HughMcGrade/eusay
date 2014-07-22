from django.test import TestCase, Client
from eusay.models import *
from .forms import UserForm
from eusay.views import generate_new_user
from django.contrib.sessions.backends.db import SessionStore

class IndexTest (TestCase):

    fixtures = ['test_fixtures.json']
    
    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposals', response.context)
        self.assertTrue(len(response.context['proposals']) > 0)

class HideTest (TestCase):
    fixtures = ['test_fixtures.json']

    def test_proposal_hide(self):
        proposal = Proposal.objects.all()[0]
        
        # Make moderator
        self.client.get('/make_mod/')

        # Hide proposal
        response = self.client.post('/hide_proposal/' + str(proposal.id), { 'reason' : 'test' })
        self.assertTrue(response.status_code, 200)
        
        # Test is hidden
        self.assertTrue(proposal.is_hidden())
        self.assertNotIn(proposal, Proposal.get_visible_proposals())
        
        # Test is not shown
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposals', response.context)
        self.assertNotIn(proposal, response.context['proposals'])

        # Test page shows hidden message
        response = self.client.get('/proposal/' + str(proposal.id) + '/' + proposal.slug)
        self.assertEqual(response.status_code, 200)
        self.assertIn('hide', response.context)
        self.assertTrue(response.context['hide'])

        # Test hidden proposals page
        response = self.client.get('/proposal_hides/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('hiddens', response.context)
        found_in_hiddens = False
        for hide in response.context['hiddens']:
            if hide.proposal == proposal:
                found_in_hiddens = True
        self.assertTrue(found_in_hiddens)

        # TODO Add unhide tests
        
    def test_non_moderator_proposal_hide(self):
        # Test hide by non-moderator
        proposal = Proposal.objects.all()[1]
        self.client.get('/add_user/')
        response = self.client.post('/hide_proposal/' + str(proposal.id), { 'reason' : 'test' })
        self.assertEqual(response.status_code, 403)
        
        # Test hide has failed
        self.assertFalse(proposal.is_hidden())
        self.assertIn(proposal, Proposal.get_visible_proposals())

    def test_comment_hide(self):
        comment = Comment.objects.all()[0]
        
        # Make moderator
        self.client.get('/make_mod/')

        # Hide proposal
        response = self.client.post('/hide_comment/' + str(comment.id), { 'reason' : 'test' })
        self.assertTrue(response.status_code, 200)
        
        # Test is hidden
        self.assertTrue(comment.is_hidden())
        self.assertNotIn(comment, comment.proposal.get_visible_comments())
        
        # Test is not shown
        response = self.client.get('/get_comments/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('comments', response.context)
        self.assertNotIn(comment, response.context['comments'])

        # Test hidden proposals page
        response = self.client.get('/comment_hides/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('hiddens', response.context)
        found_in_hiddens = False
        for hide in response.context['hiddens']:
            if hide.comment == comment:
                found_in_hiddens = True
        self.assertTrue(found_in_hiddens)

        # TODO Add unhide tests
        
    def test_non_moderator_comment_hide(self):
        # Test hide by non-moderator
        comment = Comment.objects.all()[1]
        self.client.get('/add_user/')
        response = self.client.post('/hide_proposal/' + str(comment.id), { 'reason' : 'test' })
        self.assertEqual(response.status_code, 403)
        
        # Test hide has failed
        self.assertFalse(comment.is_hidden())
        self.assertIn(comment, comment.proposal.get_visible_comments())

class VoteTest (TestCase):
    
    def setUp(self):
        self.proposer = User.objects.create(
            sid="s123456",
            name="",
            isModerator=False)
        self.proposal = Proposal.objects.create(
            title="",
            proposer=self.proposer,
            text="")
        self.comment = Comment.objects.create(
            text="",
            user=self.proposer,
            proposal=self.proposal)
       
    def test_proposal_votes(self):
        # Test vote up
        self.client.get('/vote_proposal/up/' + str(self.proposal.id))
        self.assertEqual(self.proposal.get_votes_up_count(), 1)
        self.assertEqual(self.proposal.get_votes_down_count(), 0)

        # Test cancel up vote
        self.client.get('/vote_proposal/up/' + str(self.proposal.id))
        self.assertEqual(self.proposal.get_votes_up_count(), 0)
        self.assertEqual(self.proposal.get_votes_down_count(), 0)
        
        # Test vote down
        self.client.get('/vote_proposal/down/' + str(self.proposal.id))
        self.assertEqual(self.proposal.get_votes_up_count(), 0)
        self.assertEqual(self.proposal.get_votes_down_count(), 1)
        
        # Test cancel down vote
        self.client.get('/vote_proposal/down/' + str(self.proposal.id))
        self.assertEqual(self.proposal.get_votes_up_count(), 0)
        self.assertEqual(self.proposal.get_votes_down_count(), 0)

        # Vote up
        self.client.get('/vote_proposal/up/' + str(self.proposal.id))
        
        # Get new user
        self.client.get('/add_user/')

        # Test vote up with new user
        self.client.get('/vote_proposal/up/' + str(self.proposal.id))
        self.assertEqual(self.proposal.get_votes_up_count(), 2)
        self.assertEqual(self.proposal.get_votes_down_count(), 0)
        
        # Test vote down with new user
        self.client.get('/vote_proposal/down/' + str(self.proposal.id))
        self.assertEqual(self.proposal.get_votes_up_count(), 1)
        self.assertEqual(self.proposal.get_votes_down_count(), 1)

    def test_comment_votes(self):
        # Test vote up
        self.client.get('/vote_comment/up/' + str(self.comment.id))
        self.assertEqual(self.comment.get_votes_up_count(), 1)
        self.assertEqual(self.comment.get_votes_down_count(), 0)
        
        # Test cancel up vote
        self.client.get('/vote_comment/up/' + str(self.comment.id))
        self.assertEqual(self.comment.get_votes_up_count(), 0)
        self.assertEqual(self.comment.get_votes_down_count(), 0)
        
        # Test vote down
        self.client.get('/vote_comment/down/' + str(self.comment.id))
        self.assertEqual(self.comment.get_votes_up_count(), 0)
        self.assertEqual(self.comment.get_votes_down_count(), 1)

        # Test cancel down vote
        self.client.get('/vote_comment/down/' + str(self.comment.id))
        self.assertEqual(self.comment.get_votes_up_count(), 0)
        self.assertEqual(self.comment.get_votes_down_count(), 0)

        # Vote up
        self.client.get('/vote_comment/up/' + str(self.comment.id))

        # Cannot test cancel vote as testing sessions does not work
        self.client.get('/add_user/')

        # Test vote up with new user
        self.client.get('/vote_comment/up/' + str(self.comment.id))
        self.assertEqual(self.comment.get_votes_up_count(), 2)
        self.assertEqual(self.comment.get_votes_down_count(), 0)
        
        # Test vote down with new user
        self.client.get('/vote_comment/down/' + str(self.comment.id))
        self.assertEqual(self.comment.get_votes_up_count(), 1)
        self.assertEqual(self.comment.get_votes_down_count(), 1)

class CommentTest (TestCase):
    
    fixtures = ['test_fixtures.json']

    def testGetComments(self):
        response = self.client.get('/get_comments/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('comments', response.context)
        self.assertIn('Scotland should be more #yolo!!!!', [c.text for c in response.context['comments']])
        response = self.client.get('/get_comments/1/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('comments', response.context)
        self.assertEqual(response.context['comments'][0].text, 'A reply!')
    
    def testAddComment(self):
        comment = { 'text' : 'New comment' }
        r = self.client.post('/proposal/1/eusa-should-support-scottish-independence', comment)
        response = self.client.get('/get_comments/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('comments', response.context)
        self.assertIn('New comment', [c.text for c in response.context['comments']])

class ProposalTest (TestCase):
    
    fixtures = ['test_fixtures.json']
    maxDiff = None
    
    def test_proposal(self):
        response = self.client.get('/proposal/1/eusa-should-support-scottish-independence')
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposal', response.context)
        proposal = response.context['proposal']
        self.assertEqual(proposal.title, 'EUSA should support Scottish independence')
        self.assertEqual(proposal.text, ' Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi aliquet molestie ornare. Nam auctor eget ligula ac facilisis. In hac habitasse platea dictumst. Aliquam porta, enim nec ultrices sagittis, ipsum ipsum semper tortor, sit amet dignissim felis lorem vel nibh. Aenean pellentesque magna ante, et lacinia lectus gravida sit amet. Mauris vel odio nec elit suscipit tristique non vitae lectus. Ut aliquet hendrerit purus a eleifend. ')
        comment = proposal.comments.get(id=1)
        self.assertEqual(comment.text, 'Scotland should be more #yolo!!!!')
        # TODO Test for tag once set up in fixtures

class TagTest (TestCase):
    
    fixtures = ['test_fixtures.json']
    
    def setUp(self):
        # TODO Set up tag in fixtures (then test in ProposalTest)
        self.proposal = Proposal.objects.all()[0]
        self.tag = Tag.objects.all()[0]
        self.proposal.tags.add(self.tag)

    def test_tags(self):
        response = self.client.get('/proposal/' + str(self.proposal.id) + '/' + self.proposal.slug)
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposal', response.context)
        self.assertIn(self.tag, response.context['proposal'].tags.all())
        
        response = self.client.get('/tag/' + str(self.tag.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposals', response.context)
        self.assertIn(self.proposal, response.context['proposals'])


class ValidatorsTest(TestCase):
    def setUp(self):
        User.objects.get_or_create(sid="s0000000", name="Tao Oat")

    def test_unique_user_slug(self):
        # Both "Tao Oat" and "Tao! Oat!" should slugify to "tao-oat", so the
        # following form should not be valid.
        form_data = {
            "name": "Tao! Oat!"
        }
        form = UserForm(data=form_data,
                        current_user=User(sid="s1111111", name="Whatever"))
        self.assertFalse(form.is_valid())
from django.test import TestCase, Client
from eusay.models import *
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
        response = self.client.get('/proposal/' + str(proposal.id))
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
            actionDescription="",
            backgroundDescription="",
            beliefsDescription="")
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
        self.assertEqual(response.context['comments'][0].text, 'Scotland should be more #yolo!!!!')
        response = self.client.get('/get_comments/1/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('comments', response.context)
        self.assertEqual(response.context['comments'][0].text, 'A reply!')
    
    def testAddComment(self):
        comment = { 'text' : 'New comment' }
        self.client.post('/proposal/1/', comment)
        response = self.client.get('/get_comments/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('comments', response.context)
        self.assertIn('New comment', [c.text for c in response.context['comments']])

class ProposalTest (TestCase):
    
    fixtures = ['test_fixtures.json']
    maxDiff = None
    
    def test_proposal(self):
        response = self.client.get('/proposal/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposal', response.context)
        proposal = response.context['proposal']
        self.assertEqual(proposal.title, 'EUSA should support Scottish independence')
        self.assertEqual(proposal.actionDescription, ' Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi aliquet molestie ornare. Nam auctor eget ligula ac facilisis. In hac habitasse platea dictumst. Aliquam porta, enim nec ultrices sagittis, ipsum ipsum semper tortor, sit amet dignissim felis lorem vel nibh. Aenean pellentesque magna ante, et lacinia lectus gravida sit amet. Mauris vel odio nec elit suscipit tristique non vitae lectus. Ut aliquet hendrerit purus a eleifend. ')
        self.assertEqual(proposal.backgroundDescription, ' Donec auctor felis commodo, ullamcorper libero vitae, luctus purus. Donec eu libero at eros suscipit lacinia. Phasellus nec augue at nunc viverra iaculis eget at libero. Praesent orci tellus, aliquet in felis ut, luctus semper urna. Vestibulum non lacus scelerisque, ornare nibh nec, tincidunt velit. Proin sit amet egestas diam. Sed eget aliquam diam. Duis id sagittis arcu. Pellentesque non bibendum neque. Fusce cursus eget quam a bibendum. Donec enim libero, faucibus vitae luctus tempor, venenatis a neque. Praesent nec nibh non justo sagittis viverra vitae vitae enim. Aenean vitae adipiscing arcu. ')
        self.assertEqual(proposal.beliefsDescription, ' Duis consequat mi blandit turpis tincidunt facilisis. Nullam varius faucibus quam non accumsan. Phasellus ac mattis mi, at sagittis nibh. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Sed consectetur tempus justo eget aliquam. Phasellus pharetra elit at magna placerat, sit amet luctus magna vestibulum. Proin condimentum nibh id augue pretium, et sodales neque sagittis. Curabitur ut augue dictum, sollicitudin enim sit amet, dictum mauris. Praesent quis auctor massa. Praesent mollis a purus vitae convallis. Nulla eros tortor, cursus non diam nec, hendrerit fringilla ipsum. Praesent lacus lorem, fringilla sit amet mauris quis, placerat rutrum massa. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Etiam sed viverra mi. Ut dui quam, iaculis eu dignissim et, laoreet ac turpis. Morbi scelerisque mi quis posuere accumsan. ')
        comment = proposal.comments.all()[0]
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
        response = self.client.get('/proposal/' + str(self.proposal.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposal', response.context)
        self.assertIn(self.tag, response.context['proposal'].tags.all())
        
        response = self.client.get('/tag/' + str(self.tag.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposals', response.context)
        self.assertIn(self.proposal, response.context['proposals'])

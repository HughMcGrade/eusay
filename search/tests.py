from django.test import TestCase

from eusay.models import Proposal, User, Tag


class SearchTest(TestCase):

    def setUp(self):
        """
        Create a user, tag and proposal for these tests
        """
        test_user = User.objects.create(sid="s1", username="Test User")
        test_tag = Tag.objects.create(name="Test tag")
        test_proposal = Proposal.objects.create(title="Test Proposal",
                                                text="Test text",
                                                user=test_user)
        test_proposal.tags.add(test_tag)

    def test_search_in_title(self):
        """
        See if search works in the title of proposals
        """
        test_proposal = Proposal.objects.get(title="Test Proposal")
        response = self.client.get('/search/?q=proposal')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.context)
        self.assertIn(test_proposal,
                      [p.object for p in response.context['results'] if p])

    def test_search_in_text(self):
        """
        See if search works in the text of proposals
        """
        test_proposal = Proposal.objects.get(title="Test Proposal")
        response = self.client.get('/search/?q=text')
        self.assertEqual(response.status_code, 200)
        self.assertIn(test_proposal,
                      [p.object for p in response.context['results']])

'''
    def test_search_in_tags(self):
        """
        See if search works in the tags of proposals
        """
        test_proposal = Proposal.objects.get(title="Test Proposal")
        response = self.client.get('/search/?q=tag')
        self.assertEqual(response.status_code, 200)
        self.assertIn(test_proposal,
                      [p.object for p in response.context['results']])
'''

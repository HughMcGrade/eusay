import random

from core.tests import BaseTestCase

class SearchTest(BaseTestCase):

    def test_search_in_title(self):
        """
        See if search works in the title of proposals
        """
        response = self.client.get('/search/?q=Cascada')
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposals', response.context)
        self.assertIn(self.proposal, response.context['proposals'])

    def test_search_in_text(self):
        """
        See if search works in the text of proposals
        """
        response = self.client.get('/search/?q=principal')
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposals', response.context)
        self.assertIn(self.proposal, response.context['proposals'])

'''
    def test_search_in_tags(self):
        """
        See if search works in the tags of proposals
        """
        self.proposal = Proposal.objects.get(title="Test Proposal")
        response = self.client.get('/search/?q=tag')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.proposal,
                      [p.object for p in response.context['results']])
'''

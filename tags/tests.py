from django.test import TestCase
from django.core.urlresolvers import reverse

from tags.models import Tag
from core.tests import addObjects

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

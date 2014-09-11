from django.core.urlresolvers import reverse

from tags.models import Tag
from core.tests import BaseTestCase


class TagTest (BaseTestCase):

    def testView(self):
        url = reverse('tag', args=[self.tag.id, self.tag.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('proposals', response.context)
        self.assertIn(self.proposal, response.context['proposals'])
        # TODO Test sort?

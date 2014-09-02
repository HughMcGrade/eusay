from django.test import TestCase
from django.core.urlresolvers import reverse

from comments import models
from core.tests import addObjects


class DeleteTest(TestCase):

    def setUp(self):
        addObjects(self)

    def testDeleteComment(self):
        url = reverse('delete_comment', args=[self.comment.id])

        # Log in as user other than original poster
        self.assertTrue(self.client.login(username=self.officeholder.username,
                                          password=''))

        # View page as user other than original poster
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Delete as user other than original poster
        post = {'action': 'delete'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        comment = models.Comment.objects.get(id=self.comment.id)
        self.assertNotEqual(comment.text,
                            "This comment has been deleted by its creator.")

        # Log in as original poster
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=''))

        # View page as original poster
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Delete as user other than original poster
        post = {'action': 'delete'}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.comment = models.Comment.objects.get(id=self.comment.id)
        self.assertEqual(self.comment.text,
                         "This comment has been deleted by its creator.")

# TODO add edit test

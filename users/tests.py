from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from core.tests import BaseTestCase

from users.models import User
from tags.models import Tag

class ProfileTest(BaseTestCase):

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
        post = {'username': 'Brendan', 'hasProfile': self.user.hasProfile}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 200)
        previous_name = self.user.username
        self.user = get_user_model().objects.get(id=self.user.id)
        self.assertEqual(self.user.username, previous_name)

        # Log in as self
        self.client.login(username=self.user.username, password="")

        # Change own username
        post = {'username': 'Brendan', 'hasProfile': self.user.hasProfile}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)
        self.user = get_user_model().objects.get(id=self.user.id)
        self.assertEqual(self.user.username, 'Brendan')

    def testChangeHasProfile(self):
        url = reverse('user', args=[self.user.slug])

        # Log in as another user
        self.client.login(username=self.eusa_staff.username, password="")

        # Change other user's hasProfile value
        post = {'username': self.user.username,
                'hasProfile': not self.user.hasProfile}
        response = self.client.post(url, post)
        previous_value = self.user.hasProfile
        self.user = get_user_model().objects.get(id=self.user.id)
        self.assertEqual(self.user.hasProfile, previous_value)

        # Log in as self
        self.client.login(username=self.user.username, password="")

        # Change own hasProfile value
        post = {'username': 'Brendan', 'hasProfile': not self.user.hasProfile}
        response = self.client.post(url, post)
        previous_value = self.user.hasProfile
        self.user = get_user_model().objects.get(id=self.user.id)
        self.assertEqual(self.user.hasProfile, not previous_value)

class WelcomeTest (BaseTestCase):

    def test_welcome(self):
        # Add tags
        tag1 = Tag.objects.create(name="Group1", description="A tag", group=1)
        tag2 = Tag.objects.create(name="Group2", description="Another tag", group=2)
        tag3 = Tag.objects.create(name="Group3", description="Yet another tag", group=3)

        # Login as user
        self.assertTrue(self.client.login(username=self.user.username, password=""))

        # Get prepare page
        url = reverse("prepare_new_user")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

        # Submit prepare
        new_username = 'Merkel54'
        post = {'username': new_username,
                'other_tags': str(tag3.id),
                'liberation_tags': str(tag2.id),
                'school_tags': [str(self.tag.id), str(tag1.id)]}
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 302)

        # Test effect
        user = User.objects.get(sid=self.user.sid)
        self.assertEqual(user.username, new_username)
        for tag in [self.tag, tag1, tag2, tag3]:
            self.assertIn(Tag.objects.get(id=tag.id), user.follows_tags.all())

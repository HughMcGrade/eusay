from django.conf import settings
from django.contrib.auth.backends import RemoteUserBackend
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model


class CustomUserModelBackend(RemoteUserBackend):
    def authenticate(self, remote_user):
        """
        This code is the same as the authenticate function from
        django.contrib.auth.backends.RemoteUserBackend,
        except with a way to specify our extended User model.
        The idea for the self.user_class property comes
        from Scott Barnham.

        Also, we've changed instances of `username` to `sid` since that's
        what CoSign supplies us with.
        """
        if not remote_user:
            return
        user = None
        sid = self.clean_username(remote_user)

        if self.create_unknown_user:
            user, created = \
                self.user_class.objects.get_or_create(sid=sid)
            if created:
                user = self.configure_user(user)
        else:
            try:
                user = self.user_class.objects.get(sid=sid)
            except self.user_class.DoesNotExist:
                pass
        return user

    @property
    def user_class(self):
        """
        This code was written by Scott Barnham.
        """
        if not hasattr(self, '_user_class'):
            self._user_class = \
                get_model(*settings.CUSTOM_USER_MODEL.split('.', 2))
            if not self._user_class:
                raise ImproperlyConfigured('Could not get custom user model')
        return self._user_class

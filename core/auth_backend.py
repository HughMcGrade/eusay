from django.conf import settings
from django.contrib.auth.backends import RemoteUserBackend
from users.models import User


class CustomUserModelBackend(RemoteUserBackend):
    def authenticate(self, remote_user):
        if not remote_user:
            return
        user = None
        sid = self.clean_username(remote_user)

        if self.create_unknown_user \
           and not User.objects.filter(sid=sid).exists():
            user = User.objects.create(sid=sid, username=sid)
            user = self.configure_user(user)
        else:
            try:
                user = User.objects.get(sid=sid)
            except User.DoesNotExist:
                pass
        return user

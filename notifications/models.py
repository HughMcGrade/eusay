from django.db import models
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class NotificationManager(models.Manager):
    def get_unread(self, user):
        return Notification.objects.filter(recipient=user).\
            filter(unread=True)

    def get_read(self, user):
        return Notification.objects.filter(recipient=user).\
            filter(unread=False)


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("proposal_submitted", ""),
        ("proposal_response", ""),
        ("proposal_comment", ""),
        ("proposal_amendment", ""),
        ("comment_reply", ""),
        ("student_council_soon", ""),
        ("comment_hidden", ""),
        ("proposal_hidden", ""),
        ("proposal_vote_up", ""),
        ("proposal_vote_down", ""),
        ("comment_vote_up", ""),
        ("comment_vote_down", "")
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name="notifications")
    type = models.CharField(max_length=50,
                            choices=NOTIFICATION_TYPES,
                            blank=False)
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content = GenericForeignKey()
    unread = models.BooleanField(default=True)
    has_been_emailed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = NotificationManager()

    def mark_as_read(self):
        self.unread = False
        self.save()

    def mark_as_emailed(self):
        self.has_been_emailed = True
        self.save()
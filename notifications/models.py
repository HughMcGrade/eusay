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
        ("proposal_submitted", "new proposal in"),
        ("proposal_response", "new response to"),
        ("proposal_comment", "new comment on"),
        ("proposal_amendment", "new suggested amendment to"),
        ("comment_reply", "new reply to"),
        ("student_council_soon", "student council coming up"),
        ("comment_hidden", "comment hidden"),
        ("proposal_hidden", "proposal hidden"),
        # TODO: add notifications for votes?
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
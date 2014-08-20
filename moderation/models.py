from django.db import models
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class HideAction(models.Model):
    id = models.AutoField(primary_key=True)
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL)
    createdAt = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=2000)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey()

    def save(self, *args, **kwargs):
        if not self.moderator.isModerator:
            raise Exception("Only moderators may perform hide actions!")
        else:
            super(HideAction, self).save()
            self.content.isHidden = True
            self.content.save()

    @staticmethod
    def get_hide_actions(object_id, content_type):
        return HideAction.objects.filter(content_type=content_type)\
                                 .filter(object_id=object_id)


class Report(models.Model):
    id = models.AutoField(primary_key=True)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=2000)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey()

    @staticmethod
    def get_reports(content):
        content_type = ContentType.objects.get_for_model(content)
        return Report.objects.filter(content_type=content_type)\
                             .filter(object_id=content.id)

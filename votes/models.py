from django.db import models
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.conf import settings

class VoteManager(models.Manager):
    def get_votes(self, content):
        content_type = ContentType.objects.get_for_model(content)
        return Vote.objects.filter(content_type=content_type,
                                   object_id=content.id)

    def get_votes_count(self, content, is_up):
        return self.get_votes(content).filter(isVoteUp=is_up).count()

class Vote(models.Model):
    isVoteUp = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="votes")

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey()

    objects = VoteManager()

    def save(self, *args, **kwargs):
        super(Vote, self).save(*args, **kwargs)
        self.content.upVotes = Vote.objects.get_votes_count(self.content, True)
        self.content.downVotes = Vote.objects.get_votes_count(self.content,
                                                              False)
        self.content.save()

    def delete(self, *args, **kwargs):
        if self.isVoteUp:
            self.content.upVotes = Vote.objects.get_votes_count(self.content,
                                                                True) - 1
        else:
            self.content.downVotes = Vote.objects.get_votes_count(self.content,
                                                                  False) - 1
        self.content.save()
        super(Vote, self).delete(*args, **kwargs)

    def get_content_type():
        if not hasattr(Vote, '_content_type'):
            Vote._content_type = ContentType.objects.get(
                app_label="votes", model="vote")
        return Vote._content_type

from django.db import models
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Vote(models.Model):
    isVoteUp = models.BooleanField()
    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("User")

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey()

    @staticmethod
    def get_votes(content):
        content_type = ContentType.objects.get_for_model(content)
        return Vote.objects.filter(content_type=content_type,\
                                   object_id=content.id)

    def save(self, *args, **kwargs):
        super(Vote, self).save(*args, **kwargs)
        self.content.upVotes = self.content.get_votes_count(True)
        self.content.downVotes = self.content.get_votes_count(False)
        self.content.save()

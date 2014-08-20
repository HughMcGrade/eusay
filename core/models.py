from django.db import models

class Content(models.Model):
    id = models.AutoField(primary_key=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    lastModified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey("User")
    upVotes = models.IntegerField(default=0)
    downVotes = models.IntegerField(default=0)
    isHidden = models.BooleanField(default=False)

    def get_votes_count(self, isUp):
        try:
            return len(Vote.get_votes(self).filter(isVoteUp=isUp))
        except Exception:
            return 0

    def get_votes_up_count(self):
        #return self.get_votes_count(True)
        return self.upVotes

    def get_votes_down_count(self):
        #return self.get_votes_count(False)
        return self.downVotes

    class Meta:
        abstract = True

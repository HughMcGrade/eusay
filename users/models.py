from django.db import models

class UserManager(usermodels.UserManager):

    def get_deleted_content_user(self):
        try:
            return self.get(username='Deleted Content')
        except User.DoesNotExist:
            return self.create(sid='Deleted Content',\
                               username='Deleted Content', userStatus='User')

class User(usermodels.AbstractUser):

    # The first element in each tuple is the actual value to be stored,
    # and the second element is the human-readable name.
    USER_STATUS_CHOICES = (
        ("User", "Regular User"),
        ("Staff", "EUSA Staff"),
        ("Candidate", "EUSA Candidate"),
        ("Officeholder", "EUSA Officeholder")
    )
    sid = models.CharField("student ID", max_length=20, unique=True)
    slug = models.SlugField(default="slug")
    userStatus = models.CharField("user status",
                                  max_length=12,
                                  choices=USER_STATUS_CHOICES,
                                  default="User")
    title = models.CharField(max_length=100, blank=True)
    isModerator = models.BooleanField("moderator", default=False)
    hasProfile = models.BooleanField("public profile", default=False)

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

    def proposed(self):
        return Proposal.objects.all().filter(user=self)

    def comments(self):
        return Comment.objects.all().filter(user=self)

    def save(self, *args, **kwargs):
        self.slug = better_slugify(self.username, domain="User")
        super(User, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("user", kwargs={"slug": self.slug})

    def get_vote_on(self, content):
        content_type = ContentType.objects.get_for_model(content)
        try:
            vote = Vote.objects.get(user=self, content_type=content_type,\
                                    object_id=content.id)
            if vote.isVoteUp:
                return 1
            else:
                return -1
        except Vote.DoesNotExist:
            return 0

    def get_proposals_voted_for(self):
        """
        Returns a list (formerly QuerySet) of proposals that the user
        has voted for.
        """
        user_votes = Vote.objects.filter(user=self)\
                                 .filter(content_type=Proposal.contentType())\
                                 .filter(isVoteUp=True)
        return [vote.content for vote in user_votes]

    def get_proposals_voted_against(self):
        """
        Returns a list (formerly QuerySet) of proposals that
        the user has voted against.
        """
        user_votes = Vote.objects.filter(user=self)\
                                 .filter(content_type=Proposal.contentType())\
                                 .filter(isVoteUp=False)
        return [vote.content for vote in user_votes]

    def __unicode__(self):
        return self.username + " (" + self.sid + ")"

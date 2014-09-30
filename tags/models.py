from django.db import models
from django.core.urlresolvers import reverse

from slugify import slugify


class Tag(models.Model):
    TAG_GROUPS = (
        (1, "School"),
        (2, "Liberation"),
        (3, "Other")
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(blank=False, max_length=100)
    group = models.IntegerField(choices=TAG_GROUPS, default=1)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, max_length=100)
        super(Tag, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tag", kwargs={"tagId": self.id, "slug": self.slug})

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

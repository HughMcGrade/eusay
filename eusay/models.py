'''
Created on 18 Feb 2014

@author: Hugh
'''
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
import datetime
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth import models as usermodels

from .utils import better_slugify

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(default="slug", max_length=100)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.slug = better_slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tag", kwargs={"tagId": self.id, "slug": self.slug})

    def __unicode__(self):
        return self.name

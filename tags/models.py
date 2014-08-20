from django.db import models

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

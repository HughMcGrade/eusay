from django.contrib import admin
from tags.models import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "description")
    prepopulated_fields = {'slug': ('name',), }

admin.site.register(Tag, TagAdmin)

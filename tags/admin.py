from django.contrib import admin
from eusay.models import Tag

class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    prepopulated_fields = {'slug': ('name',), }

admin.site.register(Tag, TagAdmin)

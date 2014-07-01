from django import forms
from django.contrib import admin
from eusay.models import Tag, Proposal


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


class ProposalAdmin(admin.ModelAdmin):
    exclude = ("id",)
    readonly_fields = ("title", "actionDescription", "beliefsDescription",
                       "backgroundDescription", "createdAt", "lastModified", "proposer")
    list_display = ("title", "proposer",)

admin.site.register(Tag, TagAdmin)
admin.site.register(Proposal, ProposalAdmin)
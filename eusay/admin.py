from django import forms
from django.contrib import admin
from eusay.models import Tag, Proposal, User


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


class ProposalAdmin(admin.ModelAdmin):
    exclude = ("id",)
    readonly_fields = ("title", "actionDescription", "beliefsDescription",
                       "backgroundDescription", "createdAt", "lastModified", "proposer")
    list_display = ("title", "proposer",)

    # overriding this function means that proposals cannot be
    # added from the admin panel
    def has_add_permission(self, request):
        return False


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ("sid", "name", "createdAt")
    list_display = ("sid", "name", "userStatus")

admin.site.register(Tag, TagAdmin)
admin.site.register(Proposal, ProposalAdmin)
admin.site.register(User, UserAdmin)
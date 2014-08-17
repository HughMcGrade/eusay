from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from eusay.models import Tag, Proposal


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    prepopulated_fields = {'slug': ('name',), }


class ProposalAdmin(admin.ModelAdmin):
    exclude = ("id",)
    readonly_fields = ("title",
                       "text",
                       "createdAt",
                       "lastModified",
                       "user")
    list_display = ("title", "user",)

    # overriding this function means that proposals cannot be
    # added from the admin panel
    def has_add_permission(self, request):
        return False


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ("sid", )
    list_display = ("sid", "username", "userStatus", "title")
    prepopulated_fields = {'slug': ('username',), }

admin.site.register(Tag, TagAdmin)
admin.site.register(Proposal, ProposalAdmin)
admin.site.register(get_user_model(), UserAdmin)

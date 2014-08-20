from django.contrib import admin

from proposals.models import Proposal

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

admin.site.register(Proposal, ProposalAdmin)

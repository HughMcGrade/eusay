from django.contrib import admin
from django.contrib.auth import get_user_model

class UserAdmin(admin.ModelAdmin):
    readonly_fields = ("sid", )
    list_display = ("sid", "username", "userStatus", "title")
    prepopulated_fields = {'slug': ('username',), }

admin.site.register(get_user_model(), UserAdmin)

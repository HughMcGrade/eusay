from django.contrib import admin
from django.contrib.auth import get_user_model

from .forms import UserAdminForm

class UserAdmin(admin.ModelAdmin):

    form = UserAdminForm
    
    readonly_fields = ("sid", "password")
    list_display = ("sid", "username", "userStatus", "title")
    prepopulated_fields = {'slug': ('username',), }

admin.site.register(get_user_model(), UserAdmin)

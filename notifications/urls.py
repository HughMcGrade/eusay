from django.conf.urls import patterns, include, url

from .views import notifications


urlpatterns = patterns('',
    url(r'', notifications, name="all"),
#    url(r'unread/', "notifications.html", name="unread"),
#    url(r'read/', "notifications.html", name="read"),
#    url(r'mark_all_as_read/', name="mark_all_as_read"),
)
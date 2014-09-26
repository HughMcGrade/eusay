from django.conf.urls import patterns, include, url

from .views import notifications


urlpatterns = patterns('',
    url(r'', notifications, name="all"),
)
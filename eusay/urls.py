from django.conf.urls import patterns, include, url

from eusay import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'eusay.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^add_user/', views.add_user),
    url(r'^get_users/', views.get_users),
	url(r'^$', views.index)
)

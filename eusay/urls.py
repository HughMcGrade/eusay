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
	url(r'^$', views.index),
	url(r'^submit/', views.submit),
	url(r'^thanks/', views.thanks),
	url(r'^proposal/(?P<proposalId>\d+)', views.proposal),
    url(r'^vote_proposal/(?P<ud>(up|down))/(?P<proposal_id>\d+)', views.vote_proposal),
    url(r'^vote_comment/(?P<ud>(up|down))/(?P<comment_id>\d+)', views.vote_comment),
    url(r'^post_comment/(?P<proposal_id>\d+)/(?P<field>\w+)', views.post_comment),
)
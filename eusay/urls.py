from django.conf.urls import patterns, include, url
from eusay import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'eusay.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^api/proposals/', views.ProposalList.as_view()),
    url(r'^api/proposals/(?P<id>\d+)/', views.ProposalDetail.as_view()),
    url(r'^api/proposals/(?P<id>\d+)/comments/', views.CommentList.as_view()),
    url(r'^api/comments/(?P<id>\d+)/', views.CommentDetail.as_view()),
    url(r'^api/search', views.SearchResults.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^add_user/', views.add_user),
    url(r'^get_users/', views.get_users),  # TODO: remove this, since it's for debugging
    url(r'^$', views.index),
    url(r'^submit/', views.submit),
    url(r'^thanks/', views.thanks),
    url(r'^proposal/(?P<proposalId>\d+)/$', views.proposal),
    url(r'^tag/(?P<tagId>\d+)/$', views.tag),
    url(r'^vote_proposal/(?P<ud>(up|down|get))/(?P<proposal_id>\d+)', views.vote_proposal),
    url(r'^vote_comment/(?P<ud>(up|down|get))/(?P<comment_id>\d+)', views.vote_comment),
    url(r'^get_comments/(?P<proposal_id>\d+)/(?P<reply_to>\d*)', views.get_comments),
    url(r'^about/', views.about),
    url(r'^hide_comment/(?P<comment_id>\d+)', views.hide_comment),
    url(r'^hide_proposal/(?P<proposal_id>\d+)', views.hide_proposal),
    url(r'^comment_hides', views.comment_hides),
    url(r'^proposal_hides', views.proposal_hides),
    url(r'^make_mod', views.make_mod),
    # url(r'^similar_proposals/$', views.get_similar_proposals),
    url(r'^search/', views.search)
)

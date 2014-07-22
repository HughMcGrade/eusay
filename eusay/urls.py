from django.conf.urls import patterns, include, url
from eusay import views as eusay_views
from api import views as api_views
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'eusay.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^api/proposals/$', api_views.ProposalList.as_view()),
    url(r'^api/proposals/(?P<id>\d+)/$', api_views.ProposalDetail.as_view()),
    url(r'^api/proposals/(?P<id>\d+)/comments/$', api_views.CommentList.as_view()),
    url(r'^api/comments/(?P<id>\d+)/$', api_views.CommentDetail.as_view()),
    url(r'^api/search', api_views.SearchResults.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^add_user/', eusay_views.add_user), # TODO: remove this, maybe?
    url(r'^get_users/', eusay_views.get_users),  # TODO: remove this, since it's for debugging
    url(r'^$', eusay_views.index),
    url(r'^submit/', eusay_views.submit),
    url(r'^proposal/(?P<proposalId>\d+)/(?P<slug>[\w-]*)', eusay_views.proposal,
        name="proposal"),
    url(r'^tag/(?P<tagId>\d+)/(?P<slug>[\w-]*)', eusay_views.tag, name="tag"),
    url(r'^user/(?P<slug>[\w-]+)', eusay_views.profile, name="user"),
    url(r'^vote_proposal/(?P<vote_request_type>(up|down|get))/(?P<proposal_id>\d+)', eusay_views.vote_proposal),
    url(r'^vote_comment/(?P<vote_request_type>(up|down|get))/(?P<comment_id>\d+)', eusay_views.vote_comment),
    url(r'^get_comments/(?P<proposal_id>\d+)/(?P<reply_to>\d*)', eusay_views.get_comments),
    url(r'^about/', eusay_views.about),
    url(r'^hide_comment/(?P<comment_id>\d+)', eusay_views.hide_comment),
    url(r'^hide_proposal/(?P<proposal_id>\d+)', eusay_views.hide_proposal),
    url(r'^comment_hides', eusay_views.comment_hides),
    url(r'^proposal_hides', eusay_views.proposal_hides),
    url(r'^report_comment/(?P<comment_id>\d+)', eusay_views.report_comment),
    url(r'^report_proposal/(?P<proposal_id>\d+)', eusay_views.report_proposal),
    url(r'^moderator_panel', eusay_views.moderator_panel),
    url(r'^make_mod', eusay_views.make_mod),
    url(r'^search/', eusay_views.search),
    url(r'^remove_comment/(?P<comment_id>\d+)', eusay_views.remove_comment),
    url(r'^get_messages/', eusay_views.get_messages),
)

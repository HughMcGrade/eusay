"""URL patterns for all apps"""
from django.conf.urls import patterns, include, url
from django.contrib import admin

from core import views as core_views
from proposals import views as proposal_views
from comments import views as comment_views
from moderation import views as moderation_views
from users import views as user_views
from tags import views as tag_views
from search import views as search_views

admin.autodiscover()

urlpatterns = patterns('',
    # API v1
    url(r'^api/v1/', include("api_v1.urls", namespace="api_v1")),

    # Django admin
    url(r'^admin/', include(admin.site.urls)),

    # Notifications
    url(r'notifications/',
        include("notifications.urls",
                namespace="notifications")),

    # Users
    url(r'^logout/$', user_views.logout, name="logout"),
    url(r'^login/$', user_views.login, name="login"),
    url(r'^user/(?P<slug>[\w-]+)', user_views.profile, name="user"),
    url(r'^welcome', user_views.setusername, name="setusername"),

    # Proposals
    url(r'^$', proposal_views.index, name="frontpage"),  # Front page
    url(r'^submit/', proposal_views.submit, name="submit"),
    # There are two patterns for proposal pages so that if you don't enter
    # a slug in the URL, you still get to the proposal
    url(r'^proposal/(?P<proposal_id>\d+)/$',
        proposal_views.proposal,
        name="proposal"),
    url(r'^proposal/(?P<proposal_id>\d+)/(?P<slug>[\w-]*)/$',
        proposal_views.proposal,
        name="proposal"),

    # Tags
    url(r'^tag/(?P<tagId>\d+)/(?P<slug>[\w-]*)', tag_views.tag, name="tag"),

    # Moderation
    url(r'^comment_hides', moderation_views.comment_hides,
        name="hidden_comments"),
    url(r'^proposal_hides', moderation_views.proposal_hides,
        name="hidden_proposals"),
    url(r'^moderator_panel', moderation_views.moderator_panel,
        name="moderator_panel"),
    url(r'^search/', search_views.search),

    # Action URLs
    url(r'^add_user/', user_views.add_user),  # TODO: remove this, maybe?
    url(r'^get_users/', user_views.get_users),   # TODO: remove this
    url(r'^report_comment/(?P<comment_id>\d+)',
        moderation_views.report_comment,
        name="report_comment"),
    url(r'^report_proposal/(?P<proposal_id>\d+)',
        moderation_views.report_proposal,
        name="report_proposal"),
    url(r'^make_mod', user_views.make_mod),
    url(r'^make_staff', user_views.make_staff),
    # url(r'^get_messages/', _views.get_messages),
    url(r'^hide_comment/(?P<comment_id>\d+)',
        moderation_views.hide_comment,
        name="hide_comment"),
    url(r'^hide_proposal/(?P<proposal_id>\d+)',
        moderation_views.hide_proposal,
        name="hide_proposal"),
    url(r'^proposal/(?P<proposal_id>\d+)/(?P<slug>[\w-]*)/respond/$',
        proposal_views.respond_to_proposal,
        name="respond"),
    url(r'^amend_proposal/(?P<proposal_id>\d+)',
        proposal_views.amend_proposal,
        name="amend_proposal"),
    url(r'^delete_proposal/(?P<proposal_id>\d+)',
        proposal_views.delete_proposal,
        name="delete_proposal"),
    url(r'^update_proposal_status/(?P<proposal_id>\d+)',
        proposal_views.update_proposal_status,
        name="update_proposal_status"),
    url(r'^delete_comment/(?P<comment_id>\d+)',
        comment_views.delete_comment,
        name="delete_comment"),
    url(r'^edit_comment/(?P<comment_id>\d+)/$',
        comment_views.edit_comment,
        name="edit_comment"),
    url(r'^edit_response/(?P<response_id>\d+)',
        proposal_views.edit_response,
        name="edit_response"),
    url(r'^share/(?P<proposal_id>\d+)',
        proposal_views.share,
        name="share"),

    # Other
    url(r'^about/', core_views.about, name="about"),
)

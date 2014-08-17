from django.conf.urls import patterns, include, url
from django.contrib import admin

from eusay import views as eusay_views
from search import views as search_views

admin.autodiscover()

urlpatterns = patterns('',
    # API v1
    url(r'^api/v1/', include("api_v1.urls", namespace="api_v1")),

    # Django admin
    url(r'^admin/', include(admin.site.urls)),

    # Authentication
    url(r'^logout/$', eusay_views.logout, name="logout"),
    url(r'^login/$', eusay_views.login, name="login"),

    # Proposals
    url(r'^$', eusay_views.index, name="frontpage"),  # Front page
    url(r'^submit/', eusay_views.submit, name="submit"),
    url(r'^proposal/(?P<proposalId>\d+)/(?P<slug>[\w-]*)/$',
        eusay_views.proposal,
        name="proposal"),

    # Tags
    url(r'^tag/(?P<tagId>\d+)/(?P<slug>[\w-]*)', eusay_views.tag, name="tag"),

    # Profiles
    url(r'^user/(?P<slug>[\w-]+)', eusay_views.profile, name="user"),

    # Moderation
    url(r'^comment_hides', eusay_views.comment_hides, name="hidden-comments"),
    url(r'^proposal_hides', eusay_views.proposal_hides,
        name="hidden-proposals"),
                       url(r'^moderator_panel', eusay_views.moderator_panel, name="moderator_panel"),
    url(r'^search/', search_views.search),

    # Action URLs
    url(r'^add_user/', eusay_views.add_user), # TODO: remove this, maybe?
    url(r'^get_users/', eusay_views.get_users),  # TODO: remove this, since it's for debugging
    url(r'^report_comment/(?P<comment_id>\d+)',
        eusay_views.report_comment,
        name="report_comment"),
    url(r'^report_proposal/(?P<proposal_id>\d+)',
        eusay_views.report_proposal,
        name="report_proposal"),
    url(r'^make_mod', eusay_views.make_mod),
    url(r'^make_staff', eusay_views.make_staff),
    url(r'^get_messages/', eusay_views.get_messages),
    url(r'^hide_comment/(?P<comment_id>\d+)',
        eusay_views.hide_comment,
        name="hide_comment"),
    url(r'^hide_proposal/(?P<proposal_id>\d+)',
        eusay_views.hide_proposal,
        name="hide_proposal"),
    url(r'^proposal/(?P<proposalId>\d+)/(?P<slug>[\w-]*)/respond/$',
        eusay_views.respond_to_proposal,
        name="respond"),
    url(r'^amend_proposal/(?P<proposal_id>\d+)',
        eusay_views.amend_proposal,
        name="amend_proposal"),
    url(r'^delete_proposal/(?P<proposal_id>\d+)',
        eusay_views.delete_proposal,
        name="delete_proposal"),
    url(r'^delete_comment/(?P<comment_id>\d+)',
        eusay_views.delete_comment,
        name="delete_comment"),

    # Other
    url(r'^about/', eusay_views.about, name="about"),
)

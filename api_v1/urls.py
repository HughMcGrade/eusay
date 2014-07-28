from django.conf.urls import patterns, url, include
import rest_framework

import api_v1.views as api_v1_views


urlpatterns = patterns("",
    url(
        r'^proposals/$',
        api_v1_views.ProposalList.as_view(), name="proposals",
    ),
    url(
        r'^proposals/(?P<id>\d+)/$',
        api_v1_views.ProposalDetail.as_view(),
    ),
    url(
        r'^proposals/(?P<id>\d+)/comments/$',
        api_v1_views.CommentList.as_view()
    ),
    # In templates, use {% url "api_v1:similarproposals" proposal.id %}
    url(
        r'^proposals/(?P<id>\d+)/similar/$',
        api_v1_views.SimilarProposals.as_view(),
        name="similarproposals"
    ),
    url(
        r'^comments/(?P<id>\d+)/$',
        api_v1_views.CommentDetail.as_view()
    ),
    url(
        r'^search',
        api_v1_views.SearchResults.as_view()
    ),
    # In templates, use {% url "api_v1:autocomplete" proposal.id %}
    url(
        r'^autocomplete',
        api_v1_views.autocomplete,
        name="autocomplete"
    ),
    url(
        r'^auth/',
        include('rest_framework.urls',
                namespace='rest_framework')
    ),
)

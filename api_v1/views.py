import json

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from rest_framework import generics
from haystack.query import SearchQuerySet

from proposals.models import Proposal
from comments.models import Comment
from core.utils import to_queryset
from .serializers import ProposalListSerializer, ProposalDetailSerializer, \
    CommentDetailSerializer, CommentListSerializer


class ProposalList(generics.ListAPIView):
    """
    View a list of proposals.
    """
    queryset = Proposal.objects.all()
    serializer_class = ProposalListSerializer
    paginate_by = 5


class ProposalDetail(generics.RetrieveAPIView):
    """
    View a proposal's details.
    """
    queryset = Proposal.objects.all()
    serializer_class = ProposalDetailSerializer
    lookup_field = 'id'  # proposal id


class CommentList(generics.ListAPIView):
    """
    View the comments of a specific proposal.
    """
    lookup_field = 'id'  # proposal id
    serializer_class = CommentListSerializer

    def get_queryset(self):
        """
        This view should return a list of all the comments
        for a particular proposal.
        """
        proposal_id = self.kwargs['id']  # kwarg from URL
        return Comment.objects.filter(proposal__id=proposal_id)


class CommentDetail(generics.RetrieveAPIView):
    """
    View a single comment.
    """
    serializer_class = CommentDetailSerializer
    queryset = Comment.objects.all()
    lookup_field = 'id'  # comment id


class SearchResults(generics.ListAPIView):
    """
    View search results.
    """
    serializer_class = ProposalListSerializer
    paginate_by = 5

    def get_queryset(self):
        """
        Return a QuerySet of results.
        """
        queryset = Proposal.objects.none()  # empty queryset by default
        query = self.request.QUERY_PARAMS.get('q')
        if query:
            searchqueryset = SearchQuerySet().all().filter(content=query)
            queryset = to_queryset(searchqueryset)
        return queryset


class SimilarProposals(SearchResults):
    """
    View proposals similar to the input, using Haystack's more_like_this.
    """
    lookup_field = 'id'  # proposal id

    def get_queryset(self):
        """
        Return search results.
        """
        proposal_id = self.kwargs['id']
        proposal = Proposal.objects.get(id=proposal_id)
        queryset = Proposal.objects.none()  # empty queryset by default
        if proposal_id:
            searchqueryset = SearchQuerySet().more_like_this(proposal)
            queryset = to_queryset(searchqueryset)
        return queryset


def autocomplete(request):
    """
    View proposals containing the input string in the title.
    (For autocomplete)
    """
    query = request.GET.get("term", "")
    searchqueryset = SearchQuerySet().autocomplete(title_auto=query)
    suggestions = []
    for result in searchqueryset:
        title = result.title
        url = reverse("proposal",
                      kwargs={"proposal_id": result.pk, "slug": result.slug})
        suggestions.append({"label": title, "link": url})
    data = json.dumps({
        "results": suggestions
    })
    return HttpResponse(data, content_type="application/json")

from rest_framework import generics
from haystack.query import SearchQuerySet

from eusay.models import Proposal, Comment
from .serializers import ProposalListSerializer, ProposalDetailSerializer, CommentDetailSerializer,\
    CommentListSerializer

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
        proposalId = self.kwargs['id']  # kwarg from URL
        return Comment.objects.filter(proposal__id=proposalId)


class CommentDetail(generics.RetrieveAPIView):
    """
    View a single comment.
    """
    serializer_class = CommentDetailSerializer
    queryset = Comment.objects.all()
    lookup_field = 'id'  # comment id

class SearchResults(generics.ListAPIView):
    serializer_class = ProposalListSerializer
    paginate_by = 5
    def get_queryset(self):
        """
        Return search results.
        """
        def to_queryset(searchqueryset):
            """
            This helper function converts a SearchQuerySet (from the search)
            into a QuerySet.
            We don't use a generator here because pagination requires that you can
            take the len() of a list, a generators don't have a len().
            """
            return [item.object for item in searchqueryset]

        queryset = Proposal.objects.none()  # empty queryset by default
        query = self.request.QUERY_PARAMS.get('q')
        if query:
            queryset = to_queryset(SearchQuerySet().all().filter(content=query))
        return queryset
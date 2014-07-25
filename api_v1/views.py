from rest_framework import generics
from haystack.query import SearchQuerySet

from eusay.models import Proposal, Comment
from eusay.utils import to_queryset
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
            queryset = to_queryset(SearchQuerySet().all().filter(content=query))
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
            queryset = to_queryset(SearchQuerySet().more_like_this(proposal))
        return queryset
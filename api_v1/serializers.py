from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from proposals.models import Proposal
from comments.models import Comment


class CommentDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment


class CommentListSerializer(serializers.ModelSerializer):
    # The reason there are two comment serializers is so that when retrieving
    # a list of comments for a proposal, you don't need to see the "proposal"
    # field on each of them
    class Meta:
        model = Comment
        fields = ("id", "user", "text", "createdAt", "lastModified", "replyTo")


class ProposalDetailSerializer(serializers.ModelSerializer):
    comments = CommentListSerializer(many=True)

    class Meta:
        model = Proposal
        lookup_field = 'id'
        fields = ("id", "title", "text", "user",
                  "createdAt", "lastModified", "comments", "upVotes",
                  "downVotes")


class ProposalListSerializer(serializers.ModelSerializer):
    # again, there are two proposal serializers because you don't need to see
    # the description fields or comments when viewing a list of proposals

    class Meta:
        model = Proposal
        lookup_field = 'id'
        fields = ("id", "title", "user", "createdAt", "lastModified",
                  "upVotes", "downVotes")

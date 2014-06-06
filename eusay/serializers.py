from rest_framework import serializers
from eusay.models import Proposal, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment


class ProposalListSerializer(serializers.ModelSerializer):
    votesUp = serializers.IntegerField(source="get_votes_up_count", read_only=True)
    votesDown = serializers.IntegerField(source="get_votes_down_count", read_only=True)

    class Meta:
        model = Proposal
        lookup_field = 'id'


class ProposalDetailSerializer(serializers.ModelSerializer):
    votesUp = serializers.IntegerField(source="get_votes_up_count", read_only=True)
    votesDown = serializers.IntegerField(source="get_votes_down_count", read_only=True)
    comments = CommentSerializer(many=True)

    class Meta:
        model = Proposal
        lookup_field = 'id'
        fields = ("id", "title", "votesUp", "votesDown", "actionDescription", "backgroundDescription",
                  "beliefsDescription", "proposer", "createdAt", "lastModified", "comments")
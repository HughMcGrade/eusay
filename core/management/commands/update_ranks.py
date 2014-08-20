from django.core.management.base import BaseCommand
from proposals.models import Proposal
from comments.models import Comment

from datetime import datetime


class Command(BaseCommand):
    help = "Updates the ranks of all proposals and comments."

    def handle(self, *args, **kwargs):
        for proposal in Proposal.objects.all():
            proposal.rank = proposal.get_rank()
            proposal.save()
        for comment in Comment.objects.all():
            comment.rank = comment.get_score()
            comment.save()
        self.stdout.write(datetime.now().isoformat() +
                          " Successfully updated ranks")

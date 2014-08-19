from django.core.management.base import BaseCommand
from eusay.models import Proposal


class Command(BaseCommand):
    help = "Updates the ranks of all proposals."

    def handle(self, *args, **kwargs):
        for proposal in Proposal.objects.all():
            proposal.rank = proposal.get_rank()
            proposal.save()

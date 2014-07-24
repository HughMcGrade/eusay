from celery import shared_task

from .models import Proposal, Comment, Vote


#def update_proposal_ranks():
#    for proposal in Proposal.objects.all():

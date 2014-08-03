from celery import shared_task
from celery.utils.log import get_task_logger

from .models import Proposal


logger = get_task_logger(__name__)

@shared_task(ignore_result=True)
def update_proposal_ranks():
    """
    Update the rank fields of proposals

    :return: True if successful
    """
    count = 0
    for proposal in Proposal.objects.all():
        proposal.rank = proposal.get_score()
        proposal.save()
        count += 1
    logger.info('Updated ranks of %s proposals.' % str(count))
    return True
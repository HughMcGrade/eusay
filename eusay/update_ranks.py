from .models import Proposal

import logging


def update_proposal_ranks():
    """
    Update the rank fields of proposals

    :return: True if successful
    """
    count = 0
    for proposal in Proposal.objects.all():
        proposal.rank = proposal.get_rank()
        proposal.save()
        count += 1
    # TODO: logging
    return True

if __name__ == "__main__":
    update_proposal_ranks()
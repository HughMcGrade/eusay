from django.db.models.signals import post_save
from django.dispatch import receiver

from eusay.models import Response, Comment
from .models import Notification


@receiver(post_save, sender=Response)
def notify_of_response(**kwargs):
    response = kwargs.get("instance")
    voters = response.proposal.get_voters()
    proposer = response.proposal.user
    # Make sure the proposer doesn't get notified twice
    if proposer in voters:
        voters = voters.exclude(id=proposer.id)
    type = "proposal_response"
    content = response.proposal
    Notification.objects.create(recipient=proposer,
                                type=type,
                                content=content)
    for voter in voters:
        Notification.objects.create(recipient=voter,
                                    type=type,
                                    content=content)


@receiver(post_save, sender=Comment)
def notify_proposer_of_comment(**kwargs):
    comment = kwargs.get("instance")
    recipient = comment.proposal.user
    # Don't send this notification if someone replies to a proposer's own
    # comment on their own proposal, since they'll get a notification of a
    # reply anyway.
    if (not comment.replyTo) or (comment.replyTo.user != recipient):
        content = comment.proposal
        if comment.isAmendment:
            type = "proposal_amendment"
        else:
            type = "proposal_comment"
        Notification.objects.create(recipient=recipient,
                                    type=type,
                                    content=content)


@receiver(post_save, sender=Comment)
def notify_commenter_of_reply(**kwargs):
    comment = kwargs.get("instance")
    if comment.replyTo is not None:
        recipient = comment.replyTo.user
        type = "comment_reply"
        content = comment.replyTo
        Notification.objects.create(recipient=recipient,
                                    type=type,
                                    content=content)


@receiver(post_save, sender=Comment)
def notify_commenter_of_reply_in_thread(**kwargs):
    comment = kwargs.get("instance")
    recipients
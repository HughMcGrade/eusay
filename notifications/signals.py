import datetime

from django.db.models.signals import pre_save, post_save, m2m_changed, pre_delete
from django.dispatch import receiver

from proposals.models import Response, Proposal
from comments.models import Comment
from moderation.models import HideAction
from votes.models import Vote
from .models import Notification
from core.utils import remove_duplicates


@receiver(m2m_changed, sender=Proposal.tags.through)
def notify_of_new_proposal(**kwargs):
    proposal = kwargs.get("instance")
    if (datetime.datetime.now() - proposal.createdAt)\
            < datetime.timedelta(minutes=1):
        tags = proposal.tags.all()
        recipients = []
        for tag in tags:
            recipients.extend([r for r in tag.followers.exclude
                               (id=proposal.user.id)])
        recipients = remove_duplicates(recipients)
        for recipient in recipients:
            Notification.objects.create(recipient=recipient,
                                        type="new_proposal",
                                        content=proposal)


@receiver(post_save, sender=Response)
def notify_of_response(created, **kwargs):
    response = kwargs.get("instance")
    voters = response.proposal.get_voters()
    proposer = response.proposal.user
    # Don't send a notification if the response was written by the proposer
    if created and response.user != proposer:
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
def notify_proposer_of_comment(created, **kwargs):
    comment = kwargs.get("instance")
    recipient = comment.proposal.user
    # Don't send a notification if a user comments on their own proposal
    if created and comment.user != recipient:
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
def notify_commenter_of_reply(created, **kwargs):
    comment = kwargs.get("instance")
    # Only send a notification if it's a reply
    if created and comment.replyTo:
        recipient = comment.replyTo.user
        # Don't send a notification to the user who submitted the reply
        # nor the proposer.
        if recipient != comment.user and recipient != comment.proposal.user:
            type = "comment_reply"
            content = comment.replyTo
            Notification.objects.create(recipient=recipient,
                                        type=type,
                                        content=content)


@receiver(post_save, sender=Comment)
def notify_commenter_of_reply_in_thread(created, **kwargs):
    comment = kwargs.get("instance")
    if created and comment.replyTo:
        # Don't notify the parent comment's submitter if they reply to their
        # own comment. Also don't notify the proposer.
        recipients = [reply.user for reply in comment.replyTo.get_replies()
                      if reply.user != comment.user
                      and reply.user != comment.proposal.user]
        type = "comment_reply"
        content = comment.replyTo
        for recipient in recipients:
            Notification.objects.create(recipient=recipient,
                                        type=type,
                                        content=content)


@receiver(post_save, sender=Comment)
def notify_voters_of_comment(created, **kwargs):
    comment = kwargs.get("instance")
    if created:
        proposal = comment.proposal
        # Do not notify proposers or commenters notified elsewhere
        notified = [c.user for c in Comment.objects.filter(proposal=proposal)]
        notified.append(proposal.user)
        for vote in Vote.objects.filter(content_type=Proposal
                                        .get_content_type())\
                                .filter(object_id=proposal.id):
            if not vote.user in notified:
                Notification.objects.create(recipient=vote.user,
                                            type="proposal_comment",
                                            content=proposal)


@receiver(post_save, sender=Comment)
def notify_commenters_of_comment(created, **kwargs):
    comment = kwargs.get("instance")
    if created:
        for comment in Comment.objects.filter(proposal=comment.proposal).\
                exclude(user=comment.user):
            # Do not notify proposer
            if comment.user != comment.proposal.user:
                Notification.objects.create(recipient=comment.user,
                                            type="proposal_comment",
                                            content=comment.proposal)


@receiver(pre_delete, sender=Comment)
def delete_notify_of_comment(**kwargs):
    comment = kwargs.get("instance")
    Notification.objects.filter(content_type=comment.content_type,
                                object_id=comment.id).delete()


@receiver(post_save, sender=Vote)
def notify_of_vote(created, **kwargs):
    vote = kwargs.get("instance")
    recipient = vote.content.user
    if created and vote.user != recipient:
        # Votes on proposals
        if vote.content_type == Proposal.get_content_type():
            if vote.isVoteUp:
                type = "proposal_vote_up"
            else:
                type = "proposal_vote_down"

        # Votes on comments
        elif vote.content_type == Comment.get_content_type():
            if vote.isVoteUp:
                type = "comment_vote_up"
            else:
                type = "comment_vote_down"

        Notification.objects.create(recipient=recipient,
                                    type=type,
                                    content_type=Vote.get_content_type(),
                                    object_id=vote.id)


@receiver(pre_delete, sender=Vote)
def delete_notify_of_vote(**kwargs):
    # TODO: are all these conditions necessary? would it not be enough to just
    # delete any notifications where object_id=vote.id and
    # content_type=vote.content_type?
    vote = kwargs.get("instance")
    recipient = vote.content.user
    # Votes on proposals
    if vote.content_type == Proposal.get_content_type():
        if vote.isVoteUp:
            type = "proposal_vote_up"
        else:
            type = "proposal_vote_down"
    # Votes on comments
    elif vote.content_type == Comment.get_content_type():
        if vote.isVoteUp:
            type = "comment_vote_up"
        else:
            type = "comment_vote_down"
    Notification.objects.filter(recipient=recipient,
                                type=type,
                                content_type=vote.get_content_type(),
                                object_id=vote._id).delete()


@receiver(post_save, sender=HideAction)
def notify_submitter_if_content_hidden(created, **kwargs):
    hide_action = kwargs.get("instance")
    if created:
        # Don't notify submitter if they hide their own content
        if hide_action.moderator != hide_action.content.user:
            recipient = hide_action.content.user
            if hide_action.content_type == Proposal.get_content_type():
                type = "proposal_hidden"
            elif hide_action.content_type == Comment.get_content_type():
                type = "comment_hidden"
            Notification.objects.create(recipient=recipient,
                                        type=type,
                                        content=hide_action.content)

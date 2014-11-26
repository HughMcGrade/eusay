from django.contrib.contenttypes.models import ContentType

from votes.models import Vote

# Doesn't render anything


def do_vote(user, content, vote_request):
    try:
        content_type = ContentType.objects.get_for_model(content)
        old_vote = Vote.objects.get(user=user,
                                    object_id=content.id,
                                    content_type=content_type)
        vote_was_up = old_vote.isVoteUp
        old_vote.delete()
        new_vote = False
    except:
        new_vote = True

    vote = Vote(user=user, content=content)

    if new_vote:
        if vote_request == "up":
            vote.isVoteUp = True
            vote.save()
            return 1
        elif vote_request == "down":
            vote.isVoteUp = False
            vote.save()
            return -1

    elif not new_vote:
        if vote_request == "up":
            if vote_was_up:
                return 0
            else:
                vote.isVoteUp = True
                vote.save()
                return 1
        elif vote_request == "down":
            if not vote_was_up:
                return 0
            else:
                vote.isVoteUp = False
                vote.save()
                return -1
    else:
        raise Exception("Unknown vote request " + str(vote_request))

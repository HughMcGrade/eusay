from django.contrib.contenttypes.models import ContentType

from votes.models import Vote

# Doesn't render anything

def do_vote(user, content, vote_request):
    try:
        content_type = ContentType.objects.get_for_model(content)
        vote = Vote.objects.get(user=user,
                                object_id=content.id,
                                content_type=content_type)
        # Test for cancel vote
        if (vote_request == "up" and vote.isVoteUp)\
           or (vote_request == "down" and not vote.isVoteUp):
            vote.delete()
            return 0
    except Vote.DoesNotExist:
        vote = Vote(user=user, content=content)

    if vote_request == "up":
        vote.isVoteUp = True
        vote.save()
        return 1
    elif vote_request == "down":
        vote.isVoteUp = False
        vote.save()
        return -1
    else:
        raise Exception("Unknown vote request " + str(vote_request))

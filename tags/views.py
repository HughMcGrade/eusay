from django.shortcuts import render
from tags.models import Tag
from proposals.models import Proposal

from django.http.response import HttpResponsePermanentRedirect,\
    HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse


def tag(request, tagId, slug):
    tag = Tag.objects.get(id=tagId)

    # redirect requests with the wrong slug to the correct page
    if not slug == tag.slug:
        return HttpResponsePermanentRedirect(tag.get_absolute_url())

    template = "tag.html"  # main HTML
    proposals_template = "proposal_list.html"  # just the proposals

    # sort by popularity by default
    proposals = Proposal.objects.get_visible_proposals(tag=tag, sort="popular")
    sort = "popular"

    if request.GET.get("sort") == "newest":
        proposals = Proposal.objects.get_visible_proposals(
            tag=tag, sort="newest")
        sort = "newest"

    context = {
        "proposals": proposals,
        "proposals_template": proposals_template,
        "tag": tag,
        "sort": sort,
    }
    # TODO if we find the JS approach is okay, change this:
    # ajax requests only return the proposals, not the whole page
    if request.is_ajax():
        template = proposals_template
    return render(request, template, context)


def tags_list(request):
    tags = Tag.objects.all()
    if request.user.is_authenticated():
        followed_tags = request.user.follows_tags.all()
    else:
        followed_tags = []
    return render(request, "tags.html", {"tags": tags,
                                         "followed_tags": followed_tags})


def follow_tag(request, tag_id):
    tag = Tag.objects.get(id=tag_id)
    if request.user.is_authenticated():
        if tag in request.user.follows_tags.all():
            request.user.follows_tags.remove(tag)
        else:
            request.user.follows_tags.add(tag)
    else:
        messages.add_message(request, messages.ERROR, "You must be logged in "
                                                      "to follow a tag.")
    return HttpResponseRedirect(reverse("tag", args=[tag.id, tag.slug]))
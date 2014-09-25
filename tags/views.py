from django.shortcuts import render
from tags.models import Tag
from proposals.models import Proposal

from django.http.response import HttpResponsePermanentRedirect

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

from django.shortcuts import render

from haystack.query import SearchQuerySet

from proposals.models import Proposal


def search(request):
    template = "search/search.html"
    proposals_template = "proposal_list.html"
    context = {
        "proposals_template": proposals_template,
    }

    if request.method == "GET":
        if "q" in request.GET:
            query = str(request.GET.get("q"))
            results = [r.pk for r in
                       SearchQuerySet().filter(content=query).load_all()]
            # Convert to QuerySet and remove hidden proposals
            results_qs = Proposal.objects.filter(id__in=results)\
                .filter(isHidden=False)
            results_qs.filter(isHidden=False)
            context["query"] = query
            context["proposals"] = results_qs

    if request.is_ajax() and 'page' in request.GET:
        # AJAX request for pagination
        template = proposals_template

    return render(request, template, context)
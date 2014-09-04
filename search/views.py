from django.shortcuts import render

from haystack.query import SearchQuerySet


def search(request):
    template = "search/search.html"
    proposals_template = "proposal_list.html"
    context = {
        "proposals_template": proposals_template,
    }

    if request.method == "GET":
        if "q" in request.GET:
            query = str(request.GET.get("q"))
            results = [r.object for r in
                       SearchQuerySet().filter(content=query).load_all()]
            context["query"] = query
            context["proposals"] = results

    if request.is_ajax() and 'page' in request.GET:
        # AJAX request for pagination
        template = proposals_template

    return render(request, template, context)

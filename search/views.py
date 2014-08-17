from django.shortcuts import render

from haystack.query import SearchQuerySet


def search(request):
    if request.method == "GET":
        if "q" in request.GET:
            query = str(request.GET.get("q"))
            results = SearchQuerySet().all().filter(content=query).load_all()
    return render(request, "search/search.html", {"results": results})

from django.shortcuts import render

from haystack.query import SearchQuerySet

from eusay.views import get_current_user


def search(request):
    user = get_current_user(request)
    if request.method == "GET":
        if "q" in request.GET:
            query = str(request.GET.get("q"))
            results = SearchQuerySet().all().filter(content=query)
    return render(request, "search/search.html", {"user": user,
                                                  "results": results})
from collections import Counter

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from users.views import request_login
from .models import Notification


def notifications(request):
    if not request.user.is_authenticated():
        request_login(request)
        return HttpResponseRedirect(reverse("frontpage"))
    else:
        template = "notifications.html"

        if request.is_ajax():
            template = "popover_notifications.html"

        unread = Notification.objects.get_unread(request.user)
        read = Notification.objects.get_read(request.user)

        # QuerySets are evaluated lazily, so it's important that we evaluate
        # the read notifications before the unread ones are marked as read.
        # Otherwise, unread notifications will show up in both QuerySets.

        # Returns a Counter dict of the format
        # {(type of notification, relevant content): number of notifications}
        read_notifications = Counter([(n.type, n.content) for n in read])

        unread_notifications = Counter([(n.type, n.content) for n in unread])

        for n in unread:
            n.mark_as_read()
        return render(request,
                      template,
                      {"read": read_notifications.items(),
                       "unread": unread_notifications.items()})

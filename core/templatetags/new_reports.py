from django import template

from moderation.models import Report

register = template.Library()


@register.simple_tag
def new_reports():
    count = Report.objects.all().count()
    if count > 0:
        return "<span class=\"badge\">" + str(count) + "</span>"
    else:
        return ""

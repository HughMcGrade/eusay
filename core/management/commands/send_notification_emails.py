from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.defaultfilters import pluralize
from django.template.loader import render_to_string

from datetime import datetime
from collections import Counter

from users.models import User
from notifications.models import Notification


class Command(BaseCommand):
    help = "Sends out an email to all users who have unread notifications."

    def handle(self, *args, **kwargs):
        from_email = "noreply@eusay.eusa.ed.ac.uk"
        emails = []
        notifications_to_be_emailed = []
        for user in User.objects.all():
            notifications = Notification.objects.get_unread(user)\
                                                .filter(has_been_emailed=False)
            if notifications.exists() and user.email != "":
                notifications_dict = Counter([(n.type, n.content)
                                              for n in notifications])
                count = notifications.count()

                context = {"username": user.username,
                           "count": count,
                           "unread": notifications_dict.items()}

                text_content = render_to_string("notification_email.txt",
                                                context)
                html_content = render_to_string("notification_email.html",
                                                context)

                subject = "{0}, you have {1} new notification{2} on eusay!".\
                    format(user.username,
                           count,
                           pluralize(count))
                to_email = user.email
                msg = EmailMultiAlternatives(subject,
                                             text_content,
                                             from_email,
                                             [to_email])
                msg.attach_alternative(html_content, "text/html")
                emails.append(msg)

                notifications_to_be_emailed.extend(list(notifications))

        connection = get_connection()
        connection.send_messages(emails)

        for notification in notifications_to_be_emailed:
            notification.mark_as_emailed()

        self.stdout.write("{0}: Successfully sent {1} email{2}".format(
            datetime.now().isoformat(),
            len(emails),
            pluralize(len(emails))))

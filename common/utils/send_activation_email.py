from django.conf import settings
from django.core.mail import send_mail


class Activision:
    @staticmethod
    def send_email(subject, plain_message, html_message, email_to):
        send_mail(
            subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            [email_to],
            fail_silently=False,
            html_message=html_message,
        )

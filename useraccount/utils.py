import os
from common.utils.send_activation_email import Activision
from django.template.loader import render_to_string
from django.utils.html import strip_tags




def send_temporary_password(temp_password, template, subject, to):


    html_message = render_to_string(
        template, {"temp_password": temp_password}
    )
    plain_message = strip_tags(html_message)

    try:
        Activision.send_email(
            subject=subject, plain_message=plain_message, html_message=html_message, email_to=to
        )
    except Exception as e:
        print(f"Error sending activation email: {e}")
        raise e

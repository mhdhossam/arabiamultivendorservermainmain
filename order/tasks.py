from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO
from .models import Order

def payment_completed(order_id):
    try:
        # Retrieve the order
        order = Order.objects.get(id=order_id)

        # Email subject and body
        subject = f"Arabia - Invoice #{order.id}"
        message = "Marhaba,\nPlease find attached the invoice for your recent purchase."
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [order.user.email]

        # Render HTML to PDF
        html = render_to_string('orders/invoice.html', {'order': order})
        pdf_output = BytesIO()
        pdf_status = pisa.CreatePDF(html, dest=pdf_output)

        if pdf_status.err:
            print("Error in PDF generation")
            return False

        # Prepare the email
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list,
        )
        # Attach PDF
        email.attach(f'invoice_{order.id}.pdf', pdf_output.getvalue(), 'application/pdf')
        
        # Send email
        email.send()
        return True

    except Order.DoesNotExist:
        print("Order not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

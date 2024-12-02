# payment/urls.py
from django.urls import path
from . import views
from .views import OrderpayInstapay
from . import api
app_name = "payment"  # Add this line

urlpatterns = [
    path('instapay/', OrderpayInstapay.as_view(), name='payment-list-create'),
    path('paymobpay/<uuid:order_id>/initiate-payment/', api.initiate_payment, name='initiate-payment'),
    path('status-webhook/', api.payment_status_webhook, name='payment-status-webhook'),
    path('redirect/', api.payment_redirect, name='redirect'),
]

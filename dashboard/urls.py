from django.urls import  path
from django.urls import path, include
from .views import VendorOrderSummaryView , VendorOrderDetailsView

app_name = "dashboard"

urlpatterns = [
    path('vendor/<uuid:supplier_id>/order-summary/', VendorOrderSummaryView.as_view(), name='vendor-order-summary'),
    path('vendor/<uuid:supplier_id>/productorderdetails/', VendorOrderDetailsView.as_view(), name='vendor-product-order-details'),
]
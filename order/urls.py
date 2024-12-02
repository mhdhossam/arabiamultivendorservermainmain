from django.contrib import admin
from django.urls import path, include

from . import views

app_name = "order"

urlpatterns = [
    path("checkout/", views.CheckoutView.as_view()),
    path("orderitems/", views.OrderItemListView.as_view()),
    path("orders/", views.OrderListView.as_view()),
    path("orderdetail/<uuid:pk>", views.OrderDetailView.as_view()),
    path("addcart/", views.AddCartItemView.as_view()),
    path("updatecart/", views.UpdateCartItemView.as_view()),
    path("deletecartitem/<uuid:product_id>", views.DeleteCartItemView.as_view()),
    path("cart/details/",views.CartDetailView.as_view()),
    path("admin/pdf/<uuid:order_id>/",views.admin_order_pdf,name='admin_order_pdf')
    # path("advance/", views.OrderItemShippingAdvanceView.as_view()),
    # path("return/list/", views.OrderReturnListView.as_view()),
    # path("return/<id>/", views.OrderReturnView.as_view()),
    # path("return/<id>/approve/", views.OrderReturnApproveView.as_view()),
    # path("return/<id>/decline/", views.OrderReturnDeclineView.as_view()),
    # path("<id>/", views.OrderItemDetailView.as_view()),
]

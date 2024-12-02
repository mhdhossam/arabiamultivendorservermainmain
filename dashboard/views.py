# from stats.utils.admin.general.avg import get_avg_income
# from stats.utils.admin.general.income import (
#     get_daily_income,
#     get_monthly_income,
#     get_yearly_income,
# )
# from stats.utils.admin.products.count import (
#     get_in_stock_products_count,
#     get_out_of_stock_products_count,
# )
# from stats.utils.admin.products.new import (
#     get_daily_new_products,
#     get_monthly_new_products,
#     get_yearly_new_products,
# )
# from stats.utils.admin.products.sold import (
#     get_daily_sold_products,
#     get_monthly_sold_products,
#     get_yearly_sold_products,
# )
# from stats.utils.admin.rfq.count import (
#     get_total_approved_quotes_count,
#     get_total_pending_quotes_count,
#     get_total_quotes_count,
#     get_total_rejected_quotes_count,
# )
# from stats.utils.admin.rfq.value import (
#     get_daily_accepted_offers_value,
#     get_monthly_accepted_offers_value,
#     get_yearly_accepted_offers_value,
# )
# from stats.utils.admin.users.active import (
#     get_daily_active_users,
#     get_monthly_active_users,
#     get_yearly_active_users,
# )
# from stats.utils.admin.users.count import get_users_count
# from stats.utils.admin.users.new import (
#     get_daily_new_users,
#     get_monthly_new_users,
#     get_yearly_new_users,
# )


# def dashboard_callback(request, context):

#     if not context:
#         context = {}

#     general = {
#         "daily_income": get_daily_income(),
#         "monthly_income": get_monthly_income(),
#         "yearly_income": get_yearly_income(),
#         "avg": get_avg_income(),
#     }

#     users = {
#         "count": get_users_count(),
#         "daily_active": get_daily_active_users(),
#         "monthly_active": get_monthly_active_users(),
#         "yearly_active": get_yearly_active_users(),
#         "daily_new": get_daily_new_users(),
#         "monthly_new": get_monthly_new_users(),
#         "yearly_new": get_yearly_new_users(),
#     }

#     products = {
#         "in_stock_count": get_in_stock_products_count(),
#         "out_stock_count": get_out_of_stock_products_count(),
#         "daily_new": get_daily_new_products(),
#         "monthly_new": get_monthly_new_products(),
#         "yearly_new": get_yearly_new_products(),
#         "daily_sold": get_daily_sold_products(),
#         "monthly_sold": get_monthly_sold_products(),
#         "yearly_sold": get_yearly_sold_products(),
#     }

#     rfq = {
#         "count": get_total_quotes_count(),
#         "approved": get_total_approved_quotes_count(),
#         "rejected": get_total_rejected_quotes_count(),
#         "pending": get_total_pending_quotes_count(),
#         "daily_value": get_daily_accepted_offers_value(),
#         "monthly_value": get_monthly_accepted_offers_value(),
#         "yearly_value": get_yearly_accepted_offers_value(),
#     }

#     context.update({"general": general, "users": users, "products": products, "rfq": rfq})

#     return context


from django.db.models import Sum,F
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from order.models import OrderItem
from .serializers import VendorOrderSummarySerializer
from product.serializers import ProductSerializer
from django.utils import timezone
from datetime import timedelta

class VendorOrderSummaryView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, supplier_id):
        # Get the current date and time
        now = timezone.now()
        # Filter OrderItems by supplier
        order_items = OrderItem.objects.filter(product__supplier__id=supplier_id)

        # Aggregate total orders and total revenue
        total_orders = order_items.values('order').distinct().count() 
        # Calculate total products sold and total revenue
        total_products_count = order_items.aggregate(
            total_count=Sum('quantity')
        )['total_count'] or 0

        total_revenue = order_items.aggregate(
            revenue=Sum(F('total_price') * F('quantity'))
        )['revenue'] or 0.00

        # Calculate weekly earnings (filtering order items in the last 7 days)
        weekly_order_items = order_items.filter(order__created__gte=now - timedelta(weeks=1))
        weekly_revenue = weekly_order_items.aggregate(
            revenue=Sum(F('total_price') * F('quantity'))
        )['revenue'] or 0.00

        # Calculate monthly earnings (filtering order items in the last 30 days)
        monthly_order_items = order_items.filter(order__created__gte=now - timedelta(days=30))
        monthly_revenue = monthly_order_items.aggregate(
            revenue=Sum(F('total_price') * F('quantity'))
        )['revenue'] or 0.00

        # Return the aggregated data
        data =VendorOrderSummarySerializer({
            "total_orders": total_orders,
            "total_products_count": total_products_count,
            "total_revenue": total_revenue,
            "weekly_revenue": weekly_revenue,
            "monthly_revenue": monthly_revenue,
        }).data
        return Response(data)


class VendorOrderDetailsView(APIView):
    def get(self, request, supplier_id):
        # Get all OrderItems related to the given supplier_id
        order_items = OrderItem.objects.filter(product__supplier__id=supplier_id)

        # Prepare the data to return
        order_details = []

        for order_item in order_items:
            # Get the related order
            order = order_item.order
            customer_name = order.user.full_name 

            # Get the related product
            product_name = order_item.product.name

            # Get the order date from OrderItem's created field
            order_date = order_item.created

            # Add the information to the response data
            order_details.append({
                'order_id': order.id,
                'customer_name': customer_name,
                'product_name': product_name,
                'order_date': order_date,
                'quantity': order_item.quantity,  
                'total_price': order_item.total_price,  
            })

        # Return the order details
        return Response(order_details, status=status.HTTP_200_OK)
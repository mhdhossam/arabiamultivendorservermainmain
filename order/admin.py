import json
from django.contrib import admin
from .models import Order, OrderItem, ReturnRequest, ReturnRequestFile,Cart,CartItem
from django.db.models import Sum
from django.urls import path,reverse
from django.utils.safestring import mark_safe
from django.shortcuts import render





class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 
    readonly_fields = ('product', 'color', 'size', 'quantity', 'total_price')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False  # Prevents adding new OrderItems directly in Order
    

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created', 'is_paid', 'payment_method', 'get_total', 'shipping_status','order_pdf')
    list_filter = ('shipping_status','is_paid', 'payment_method', 'created')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('get_total', 'created', 'paid_date')
    inlines = [OrderItemInline]
    
    def order_pdf(self,obj):
        url=reverse('order:admin_order_pdf', args=[obj.id])
        return mark_safe(f'<a href="{url}" target="_blank">View Invoice</a>')
    order_pdf.short_description='Invoice'

    def get_total(self, obj):
        return obj.total_price  
    get_total.short_description = 'Total Price'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sales/', self.admin_site.admin_view(self.sales_view), name='sales_view'),
        ]
        return custom_urls + urls

    def sales_view(self, request):
        # Calculate sales data
        sales_data = (
            OrderItem.objects
            .values('product__translations__name')  # Adjust as per your Product model
            .annotate(total_sales=Sum('total_price'))
            .order_by('-total_sales')[:10]
        )
        # Convert the QuerySet to a list and handle Decimal types
        sales_data_list = []
        for item in sales_data:
            sales_data_list.append({
            'product__translations__name': item['product__translations__name'],
            'total_sales': float(item['total_sales'])  # Convert Decimal to float
        })

        sales_data_json = json.dumps(sales_data_list)
        return render(request, "admin/sales_view.html", {"sales_data": sales_data_json})
    

@admin.register(Order)
class SalesAdmin(OrderAdmin):
    change_list_template = "admin/sales_change_list.html"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'total_price',  'created')
    list_filter = ['created']
    search_fields = ('product__name', 'order__user__username')
    readonly_fields = ('total_price', 'created')


class ReturnRequestFileInline(admin.TabularInline):
    model = ReturnRequestFile
    extra = 1


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_item', 'tracking_number', 'status', 'reason', 'created')
    list_filter = ('status', 'reason', 'created')
    search_fields = ('user__username', 'tracking_number', 'order_item__product__name')
    inlines = [ReturnRequestFileInline]
    readonly_fields = ('created',)


@admin.register(ReturnRequestFile)
class ReturnRequestFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'return_request', 'evidence_file')
    search_fields = ('return_request__id',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display=('id','user','created','checked_out')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display=('id','cart','product','quantity')


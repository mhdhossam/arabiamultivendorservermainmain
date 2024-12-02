from django.contrib import admin
from .models import *
from django.utils.html import format_html

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'amount', 'created_at')
    list_filter = ('method', 'created_at')
    search_fields = ('order__id', 'pay_phone')
    readonly_fields = ('created_at',)
    actions = ['mark_as_paid']

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(is_paid=True)
        self.message_user(request, f"{updated} payment(s) marked as paid.")
    mark_as_paid.short_description = "Mark selected payments as paid"

    # Optional: Display the screenshot if available
    def screenshot_preview(self, obj):
        if obj.screenshot:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.screenshot.url)
        return "No screenshot"
    screenshot_preview.short_description = "Screenshot Preview"
    
    fieldsets = (
        (None, {
            'fields': ('order', 'method', 'amount', 'is_paid', 'created_at')
        }),
        ('Additional Info', {
            'fields': ('pay_phone', 'screenshot'),
        }),
    )

admin.site.register(Payment, PaymentAdmin)

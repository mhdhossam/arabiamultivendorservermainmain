from os import path
from django.contrib import admin
from django.shortcuts import redirect
from .models import Address, BuyerProfile, SupplierProfile, User,SupplierDocuments,Favorite
from django.utils.html import format_html
from django.contrib import messages



class IsActiveSupplierFilter(admin.SimpleListFilter):
    title = 'Active Supplier'
    parameter_name = 'is_active_supplier'

    def lookups(self, request, model_admin):
        return (
            ('True', 'Active'),
            ('False', 'Inactive'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(user__is_active=True)
        elif self.value() == 'False':
            return queryset.filter(user__is_active=False)
        return queryset

class SupplierDocumentsAdmin(admin.ModelAdmin):
    list_display = ['user']
    list_filter = (IsActiveSupplierFilter,)
    search_fields = ('user__email',) 
    fields = (
        'user',
        'front_id_display', 
        'front_id',
        'back_id_display', 
        'back_id',
        'tax_card_display', 
        'tax_card',
        'commercial_record_display', 
        'commercial_record',
        'bank_statement_display', 
        'bank_statement',
    )

    readonly_fields = (
        'front_id_display',
        'back_id_display',
        'tax_card_display',
        'commercial_record_display',
        'bank_statement_display',
    )
    def front_id_display(self, obj):
        if obj.front_id:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" alt="Front ID" style="width: 300px; height: auto;" onerror="this.onerror=null; this.alt=\'Image not available\'" />'
                '</a>',
                obj.front_id.url, obj.front_id.url
            )
        return "No image"
    front_id_display.short_description = "Front ID"

    def back_id_display(self, obj):
        if obj.back_id:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" alt="Back ID" style="width: 300px; height: auto;" onerror="this.onerror=null; this.alt=\'Image not available\'" />'
                '</a>',
                obj.back_id.url, obj.back_id.url
            )
        return "No image"
    back_id_display.short_description = "Back ID"

    def tax_card_display(self, obj):
        if obj.tax_card:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" alt="Tax Card" style="width: 300px; height: auto;" onerror="this.onerror=null; this.alt=\'Image not available\'" />'
                '</a>',
                obj.tax_card.url, obj.tax_card.url
            )
        return "No image"
    tax_card_display.short_description = "Tax Card"

    def commercial_record_display(self, obj):
        if obj.commercial_record:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" alt="Commercial Record" style="width: 300px; height: auto;" onerror="this.onerror=null; this.alt=\'Image not available\'" />'
                '</a>',
                obj.commercial_record.url, obj.commercial_record.url
            )
        return "No image"
    commercial_record_display.short_description = "Commercial Record"

    def bank_statement_display(self, obj):
        if obj.bank_statement:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" alt="Bank Statement" style="width: 300px; height: auto;" onerror="this.onerror=null; this.alt=\'Image not available\'" />'
                '</a>',
                obj.bank_statement.url, obj.bank_statement.url
            )
        return "No image"
    bank_statement_display.short_description = "Bank Statement"






class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'is_supplier','is_buyer','is_active', 'is_staff')
    list_filter = ('is_supplier','is_buyer','is_active')
    search_fields = ('email',) 



admin.site.register(Address)
admin.site.register(User ,UserAdmin)
admin.site.register(SupplierProfile)
admin.site.register(BuyerProfile)
admin.site.register(SupplierDocuments,SupplierDocumentsAdmin)
admin.site.register(Favorite)




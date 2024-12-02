from django.contrib import admin
from parler.admin import TranslatableAdmin,TranslatableModelForm
from.models import Brand,Category,Product,Review,Color,Size,ProductImage
from mptt.admin import MPTTModelAdmin
from mptt.forms import MPTTAdminForm

# Register your models here.




class CategoryAdminForm(MPTTAdminForm, TranslatableModelForm):
    pass


class CategoryAdmin(TranslatableAdmin, MPTTModelAdmin):
    form = CategoryAdminForm
    list_display = ('id', 'name', 'slug')

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}  


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id','product','user','rating','created_at')
    readonly_fields=['created_at']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra= 5



@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    inlines = [ProductImageInline]  # Include the inline here
    list_display = ('name', 'sku', 'price_after_discount', 'is_available', 'created', 'updated')
    search_fields = ('name', 'sku')
    list_filter = ('is_available', 'category', 'brand')

admin.site.register(Brand,TranslatableAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review , ReviewAdmin)
admin.site.register(Color,TranslatableAdmin)
admin.site.register(Size,TranslatableAdmin)
admin.site.register(ProductImage)
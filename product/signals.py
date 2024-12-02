from django.db.models.signals import post_save
from django.dispatch import receiver

# Import models
from .models import Product, Category, Brand, Size, Color, ProductFact, CategoryDimension, BrandDimension, SizeDimension, ColorDimension

@receiver(post_save, sender=Product)
def update_fact_table(sender, instance, created, **kwargs):
    # Fetch category translation for English (or other default language)
    category_translation = instance.category.translations.filter(language_code='en').first()
    category_name = category_translation.name if category_translation else instance.category.name  # Fallback to category's default name

    # Sync category dimensions
    category, _ = CategoryDimension.objects.update_or_create(
        name=category_name,  # Use the correct translation name or fallback
        defaults={
            'image': instance.category.image,
            'is_featured': instance.category.is_featured,
            'parent_name': instance.category.parent.name if instance.category.parent else None
        }
    )

    # Fetch brand translation for English (or other default language)
    brand_translation = instance.brand.translations.filter(language_code='en').first()
    brand_name = brand_translation.name if brand_translation else instance.brand.name  # Fallback to brand's default name

    # Sync brand dimensions
    brand, _ = BrandDimension.objects.update_or_create(
        name=brand_name,  # Use the correct translation name or fallback
        defaults={'image': instance.brand.image}
    )

    # Sync size and color fields for many-to-many relations
    color_dimensions = [ColorDimension.objects.get_or_create(name=color.name)[0] for color in instance.color.all()]
    size_dimensions = [SizeDimension.objects.get_or_create(name=size.name)[0] for size in instance.size.all()]

    # Retrieve the first image URL if available
    first_image_url = instance.images.first().image.url if instance.images.exists() else None

    # Fetch product translation for English (or other default language)
    product_translation = instance.translations.filter(language_code='en').first()
    product_name = product_translation.name if product_translation else instance.name  # Fallback to product's default name

    # Update or create ProductFact entry with new fields
    product_fact, _ = ProductFact.objects.update_or_create(
        product_id=instance.id,
        defaults={
            'category': category,
            'category_slug': instance.category.slug if instance.category else None,
            'brand': brand,
            'brand_slug': instance.brand.slug if instance.brand else None,
            'product_name': product_name,  # Use the translated name or fallback
            'product_slug': instance.slug,
            'first_image': first_image_url,
            'price_before_discount': instance.price_before_discount,
            'price_after_discount': instance.price_after_discount,
            'stock_quantity': instance.stock_quantity,
            'total_sold': instance.total_sold,
            'total_views': instance.total_views,
            'created': instance.created,
            'updated': instance.updated
        }
    )

    # Update many-to-many relationships for color and size
    product_fact.color.set(color_dimensions)
    product_fact.size.set(size_dimensions)

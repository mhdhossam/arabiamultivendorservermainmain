from django.core.management.base import BaseCommand
from product.models import Product, Category, Brand, Size, Color, ProductFact, CategoryDimension, BrandDimension, SizeDimension, ColorDimension
from django.utils.translation import get_language

class Command(BaseCommand):
    help = 'Populates the ProductFact and dimension tables with existing data'

    def handle(self, *args, **options):
        # Set the language to 'en' or your desired language
        language_code = 'en'

        # Populate CategoryDimension
        for category in Category.objects.all():
            # Get the translated name for 'en' using django-modeltranslation
            category_translation = category.get_translation(language_code)
            category_name = category_translation.name if category_translation else category.name

            CategoryDimension.objects.update_or_create(
                name=category_name,
                defaults={
                    'image': category.image,
                    'is_featured': category.is_featured,
                    'parent_name': category.parent.name if category.parent else None,
                }
            )

        # Populate BrandDimension
        for brand in Brand.objects.all():
            # Get the translated name for 'en' using django-modeltranslation
            brand_translation = brand.get_translation(language_code)
            brand_name = brand_translation.name if brand_translation else brand.name

            BrandDimension.objects.update_or_create(
                name=brand_name,
                defaults={'image': brand.image}
            )

        # Populate SizeDimension
        for size in Size.objects.all():
            SizeDimension.objects.update_or_create(name=size.name)

        # Populate ColorDimension
        for color in Color.objects.all():
            ColorDimension.objects.update_or_create(name=color.name, code=color.code)

        # Populate ProductFact
        for product in Product.objects.all():
            category_translation = product.category.get_translation(language_code) if product.category else None
            category_dimension = CategoryDimension.objects.get(name=category_translation.name) if category_translation else None

            brand_translation = product.brand.get_translation(language_code) if product.brand else None
            brand_dimension = BrandDimension.objects.get(name=brand_translation.name) if brand_translation else None
            
            # Get or create color and size dimensions
            color_dimensions = [ColorDimension.objects.get(name=color.name) for color in product.color.all()]
            size_dimensions = [SizeDimension.objects.get(name=size.name) for size in product.size.all()]
            
            # Retrieve the first image URL if available
            first_image_url = product.images.first().image.url if product.images.exists() else None

            # Create or update ProductFact with new fields
            product_fact, _ = ProductFact.objects.update_or_create(
                product_id=product.id,
                defaults={
                    'category': category_dimension,
                    'category_slug': product.category.slug if product.category else None,
                    'brand': brand_dimension,
                    'brand_slug': product.brand.slug if product.brand else None,
                    'product_name': product.get_translation(language_code).name if product.get_translation(language_code) else product.name,
                    'product_slug': product.slug,
                    'first_image': first_image_url,
                    'price_before_discount': product.price_before_discount,
                    'price_after_discount': product.price_after_discount,
                    'stock_quantity': product.stock_quantity,
                    'total_sold': product.total_sold,
                    'total_views': product.total_views,
                    'created': product.created,
                    'updated': product.updated,
                }
            )
            
            # Set Many-to-Many relationships for color and size dimensions
            product_fact.color.set(color_dimensions)
            product_fact.size.set(size_dimensions)

        self.stdout.write(self.style.SUCCESS('Successfully populated ProductFact and dimension tables with existing data'))

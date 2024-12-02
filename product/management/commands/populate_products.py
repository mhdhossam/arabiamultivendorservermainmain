import os
from django.core.management.base import BaseCommand
from faker import Faker
from product.models import Product, Category, Brand, Color, Size, ProductImage
from django.contrib.auth import get_user_model
import random
from common.utils.file_upload_paths import (
    brands_images_path,
    categories_images_path,
    product_images_path,
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with dummy products'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create unique categories
        categories = set()
        while len(categories) < 5:
            name = fake.word()
            slug = fake.slug()
            categories.add((name, slug))

        category_objects = [Category.objects.create(name=name, slug=slug) for name, slug in categories]

        # Create unique brands
        brands = set()
        while len(brands) < 5:
            name = fake.word()
            slug = fake.slug()
            brands.add((name, slug))

        brand_objects = [Brand.objects.create(name=name, slug=slug) for name, slug in brands]

        # Create unique colors
        colors = set()
        while len(colors) < 5:
            name = fake.color_name()
            code = fake.hex_color()
            colors.add((name, code))

        color_objects = [Color.objects.create(name=name, code=code) for name, code in colors]

        # Create unique sizes
        sizes = set()
        while len(sizes) < 5:
            name = fake.word()
            sizes.add(name)

        size_objects = [Size.objects.create(name=name) for name in sizes]

        for _ in range(20):
            category = random.choice(category_objects)
            brand = random.choice(brand_objects)
            product = Product.objects.create(
                name=fake.word(),
                description=fake.text(),
                sku=fake.unique.slug(),
                supplier=random.choice(User.objects.all()),
                price_before_discount=random.uniform(10.0, 100.0),
                price_after_discount=random.uniform(5.0, 95.0),
                category=category,
                brand=brand,
                stock_quantity=random.randint(0, 50),
                is_available=random.choice([True, False]),
                specifications={'weight': f"{random.randint(1, 10)}kg"}
            )
            # Create and associate images
            for _ in range(random.randint(1, 3)):
                image_file_name = f"{fake.uuid4()}.jpg"  # Or use another extension
                image_path = os.path.join("product","image", image_file_name)
                ProductImage.objects.create(
                    product=product,
                    image=image_path,  
                    alt_text=fake.sentence(),
                )
            product.color.set(random.sample(color_objects, random.randint(1, 3)))  # Randomly assign between 1 to 3 colors
            product.size.set(random.sample(size_objects, random.randint(1, 3)))  # Randomly assign between 1 to 3 sizes
            product.save()

        self.stdout.write(self.style.SUCCESS('20 dummy products created!'))

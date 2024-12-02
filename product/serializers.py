import json
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from .models import Brand,Category,Product,Review,Color,Size,ProductImage,ProductFact,CategoryDimension
from rest_framework import serializers
from django.utils.translation import get_language

class BrandSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Brand)

    class Meta:
        model = Brand
        fields = '__all__'


class CategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Category)

    class Meta:
        model = Category
        fields = '__all__'




class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    class Meta:
        model=Review
        fields=['id','user','user_name','product','rating','review_text','created_at']
        read_only_fields = ['user', 'created_at']
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    def __init__(self, *args, **kwargs):
        super(ReviewSerializer,self).__init__(*args, **kwargs)

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name']

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductImage
        fields=['id','image','alt_text']

class ProductSerializer(TranslatableModelSerializer):
    productName = serializers.CharField(source="name")
    productDescription = serializers.CharField(source="description",required=False)
    # Use PrimaryKeyRelatedField for writable actions (POST/PUT)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True)
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), write_only=True)
    color = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all(), many=True, write_only=True)
    size = serializers.PrimaryKeyRelatedField(queryset=Size.objects.all(), many=True, write_only=True)
    # Use detailed serializers for read-only actions (GET)
    category_details = CategorySerializer(source='category', read_only=True)
    brand_details = BrandSerializer(source='brand', read_only=True)
    color_details = ColorSerializer(source='color', many=True, read_only=True)
    size_details = SizeSerializer(source='size', many=True, read_only=True)

    translations = serializers.DictField(write_only=True)
    specifications = serializers.JSONField()
    reviews = ReviewSerializer(many=True, read_only=True)
    image_uploads = serializers.ListField(
        child=serializers.ImageField(), write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
    
    def get_translations(self, obj):
        # Assuming you are handling 'en' and 'ar' languages
        translations = obj.translations.all()
        translated_data = {}

        # Collect translations for each language (for example 'en' and 'ar')
        for translation in translations:
            translated_data[translation.language_code] = {
                "name": translation.name,
                "description": translation.description,
            }

        return translated_data
    def create(self, validated_data):
        print(validated_data)
        
        # Pop related fields
        translations_data = validated_data.pop('translations', {})
        
        colors = validated_data.pop('color', [])
        sizes = validated_data.pop('size', [])
        reviews_data = validated_data.pop('reviews', [])
        image_data = validated_data.pop('image_uploads', [])

        # Create the product
        product = Product.objects.create(**validated_data)

        # Handle translations as objects (Not as a dictionary)
        for lang, translation in translations_data.items():
             product.translations.create(language_code=lang, **translation)


        # Add ManyToMany relationships
        product.color.set(colors)
        product.size.set(sizes)

        # Add images
        for image in image_data:
            ProductImage.objects.create(product=product, image=image)

        # Add reviews
        for review_data in reviews_data:
            Review.objects.create(product=product, **review_data)

        return product



    def update(self, instance, validated_data):
        translations_data = validated_data.pop('translations', {})
        colors = validated_data.pop('color', [])
        sizes = validated_data.pop('size', [])
        image_data = validated_data.pop('image_uploads', [])
        reviews_data = validated_data.pop('reviews', [])

        # Update main instance
        instance = super().update(instance, validated_data)

        # Update or create translations
        
        for lang, translation in translations_data.items():
            translation_obj, created = instance.translations.get_or_create(
                language_code=lang
            )
            for field, value in translation.items():
                setattr(translation_obj, field, value)
            translation_obj.save()

        # Update ManyToMany relationships
        instance.color.set(colors)
        instance.size.set(sizes)

        # Add images
        if image_data:
            for image in image_data:
                ProductImage.objects.create(product=instance, image=image)

        return instance


class ProductMinimalSerializer(serializers.ModelSerializer):
    images=ProductImageSerializer(many=True, read_only=True)
    name = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id','name', 'price_after_discount','images']
    def get_name(self, obj):
        # Use the current language code
        language = get_language()
        # Filter the translations for the current language
        translation = obj.translations.filter(language_code=language).first()
        return translation.name if translation else None
    

class ProductFactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFact  # Fact model for optimized retrieval
        fields = "__all__"

class CategoryDimensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryDimension  # Dimension model for optimized retrieval
        fields = "__all__"

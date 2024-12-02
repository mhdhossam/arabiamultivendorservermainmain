from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from .models import HeroSlider
from rest_framework import serializers


class HeroSlidersSerializer(TranslatableModelSerializer):
    category_slug = serializers.SerializerMethodField()
    translations = TranslatedFieldsField(shared_model=HeroSlider)

    class Meta:
        model = HeroSlider
        fields = '__all__'
        extra_kwargs = {
            'category': {'write_only': True}  
        }

    def get_category_slug(self, obj):
        return obj.category.slug



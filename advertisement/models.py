from django.db import models
from parler.models import TranslatableModel,TranslatedFields
from product.models import Category
from django.utils.translation import gettext_lazy as _
from common.utils.file_upload_paths import (
    ads_images_path
)
# Create your models here.



class HeroSlider(TranslatableModel):
    category=models.ForeignKey(Category,related_name="hero_slider",on_delete=models.CASCADE)
    translations=TranslatedFields(
    image = models.ImageField(
        _("HeroSlider Image"),
        upload_to=ads_images_path,
    )
    )


    # def __str__(self):
    #     return self.name

from django.contrib import admin
from .models import HeroSlider
from parler.admin import TranslatableAdmin
# Register your models here.

admin.site.register(HeroSlider,TranslatableAdmin)
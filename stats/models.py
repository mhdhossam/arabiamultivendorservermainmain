from django.db import models

# Create your models here.
class Stats(models.Model):
    name = models.CharField(max_length=100)
    show = models.BooleanField(default=True)

    def __str__(self):
        return self.name
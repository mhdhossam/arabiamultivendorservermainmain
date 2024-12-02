from django.db import models
from django.contrib.auth.models import AbstractUser
from useraccount.models  import User


# Create your models here.

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.email}'s Wallet"
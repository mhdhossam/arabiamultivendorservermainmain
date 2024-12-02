from django.db import models
from common.validators.image_extension_validator import image_extension_validator
from common.utils.file_upload_paths import (payment_screenshoot_path)
from order.models import  Order


class Payment(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE)
    pay_phone=models.CharField(max_length=20,blank=True, null=True)
    PAYMENT_METHODS=[
        ('COD','Cash on Delivery'),
        ('INSTAPAY','Instapay'),
        ('VODAFONE_CASH','Vodafone Cash'),
        ('CARD','online card'),
    ]
    method=models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    screenshot=models.ImageField(upload_to=payment_screenshoot_path,blank=True , null=True,validators=[image_extension_validator])

    class Meta:
        ordering=['created_at']

    def __str__(self):
        return f"payment for order {self.order.id}"


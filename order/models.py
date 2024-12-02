from django.utils import timezone
import uuid
from collections.abc import Iterable
from django.db.models.signals import post_save
from django.dispatch import receiver
from common.utils.file_upload_paths import return_request_files_path
from common.validators.image_video_extension_validator import \
    image_video_extension_validator
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from product.models import Product,Color,Size
from useraccount.models import User

User = get_user_model()
PAYMENT_METHODS = [
    ('COD', 'Cash on Delivery'),
    ('INSTAPAY', 'Instapay'),
    ('VODAFONE_CASH', 'Vodafone Cash')
]



class Cart(models.Model):
    id=models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts", null=True, blank=True)
    created=models.DateTimeField(auto_now_add=True)
    checked_out = models.BooleanField(default=False)

    def  __str__(self):
        return str(self.id)
    def get_total_price(self):
        return sum(item.quantity * item.product.price_after_discount for item in self.items.all())

class CartItem(models.Model):
    id=models.UUIDField(default=uuid.uuid4, primary_key=True)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items",null=True, blank=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="cartitems",null=True, blank=True)
    quantity=models.PositiveSmallIntegerField(default=1)
    class Meta:
        unique_together = ('cart', 'product')
    def get_item_total(self):
        return self.quantity * self.product.price_after_discount


class Order(models.Model):
    class PAYMENT_CHOICES(models.TextChoices):
        COD = "COD", _("Cash on Delivery")
        INSTAPAY = "INSTAPAY", _("Instapay")
        VODAFONE_CASH = "VODAFONE_CASH", _("Vodafone Cash")
        CARD = "ONLINE_CARD",_("online card")
    class SHIPPING_STATUS_CHOICES(models.TextChoices):
        ORDERED = "OR", _("Ordered")
        PREPARING = "P", _("Preparing for Shipping")
        OTW = "OTW", _("On the way")
        DELIVERED = "DE", _("Delivered")
        RETURN="RE",_("Returned")

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("Buyer"), related_name="orders"
    )
    created = models.DateTimeField(_("Ordered Date"), auto_now_add=True)
    is_paid = models.BooleanField(_("Is Paid"), default=False)
    paymob_order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=50, blank=True, null=True)
    paid_date = models.DateTimeField(_("Paid Date"), null=True, blank=True)
    payment_method = models.CharField(
        _("Payment Method"), max_length=20, choices=PAYMENT_CHOICES.choices
    )
    shipping_status = models.CharField(
        _("Shipping Status"), max_length=10, choices=SHIPPING_STATUS_CHOICES.choices, 
        default=SHIPPING_STATUS_CHOICES.ORDERED
    )
    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Order by {self.user.full_name}"

    def get_total_order_price(self):
        self.total_price = sum(item.get_final_price() for item in self.order_items.all())
        self.save()

    def save(self, *args, **kwargs):
        # Update total price upon saving the Order instance
        if self.is_paid and not self.paid_date:
            self.paid_date = timezone.now()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, related_name="order_item", on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey(Size, related_name="order_item", on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(_("Quantity"), default=1)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    def get_total_product_price(self):
        return self.quantity * self.product.price_before_discount

    def get_total_discount_product_price(self):
        return self.quantity * self.product.price_after_discount

    def get_amount_saved(self):
        return self.get_total_product_price() - self.get_total_discount_product_price()

    def get_final_price(self):
        return self.get_total_discount_product_price() if self.product.price_after_discount else self.get_total_product_price()

    def save(self, *args, **kwargs):
        self.total_price = self.get_final_price()
        super().save(*args, **kwargs)
        # Trigger Order total update whenever an OrderItem is saved
        self.order.save()
# Signal to update Order total whenever an OrderItem is saved
@receiver(post_save, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    instance.order.get_total_order_price()


from django.core.exceptions import ValidationError
class ReturnRequest(models.Model):
    class RETURN_STATUS_CHOICES(models.TextChoices):
        NOT_REQUESTED = "NOT", _("Not Requested")
        APPLIED = "AP", _("Applied")
        DECLINED = "DEC", _("Declined by Supplier")
        APPROVED = "APR", _("Approved by Supplier")
        ON_THE_WAY = "OTW", _("On the way")
        COMPLETED = "CMP", _("Return Completed")

    class RETURN_REASON_CHOICES(models.TextChoices):
        POOR_QUALITY = "POO", _("Poor quality")
        WRONG_MATERIALS = "WRO", _("Wrong materials")
        WRONG_ADDRESS = "ADD", _("Shipped to the wrong address")

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Buyer"), null=True, blank=True)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, null=True, blank=True)
    tracking_number = models.CharField(_("Tracking Number"), unique=True, max_length=50)
    status = models.CharField(
        _("Return Status"), max_length=10, choices=RETURN_STATUS_CHOICES.choices, default=RETURN_STATUS_CHOICES.NOT_REQUESTED
    )
    reason = models.CharField(_("Return Reason"), max_length=15, choices=RETURN_REASON_CHOICES.choices)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    decline_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Return Request #{self.id}"
    def clean(self):
        if self.order_item.shipping_status not in [
            OrderItem.SHIPPING_STATUS_CHOICES.ORDERED,
            OrderItem.SHIPPING_STATUS_CHOICES.DELIVERED
        ]:
            raise ValidationError("Return requests can only be made for items that are Ordered or Delivered.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ReturnRequestFile(models.Model):
    return_request = models.ForeignKey(ReturnRequest, on_delete=models.CASCADE, related_name="files")
    evidence_file = models.FileField(
        null=True, blank=True, upload_to=return_request_files_path,
        validators=[image_video_extension_validator]
    )

    def __str__(self):
        return f"File for Return Request {self.return_request.id}"


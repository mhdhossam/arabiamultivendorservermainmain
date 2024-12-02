import uuid
from common.utils.file_upload_paths import (
    buyers_profile_pictures_path,
    suppliers_profile_pictures_path,
    suppliers_documents_path,
)
from common.validators.image_extension_validator import image_extension_validator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class Address(models.Model):
    country = models.CharField(_("Country"), max_length=50)
    state = models.CharField(_("State"), max_length=50, null=True, blank=True)
    city = models.CharField(_("City"), max_length=50, null=True, blank=True)

    postal_code = models.CharField(_("Postal Code"), max_length=15)

    address_1 = models.CharField(_("Address Line 1"), max_length=255)
    address_2 = models.CharField(_("Address Line 2"), max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.address_1}"


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    email = models.EmailField(_("Email"), max_length=255, unique=True)
    full_name = models.CharField(_("Full Name"), max_length=255,null=True,blank=True)

    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(_("Is Admin"), default=False)
    is_supplier = models.BooleanField(_("Is Supplier"), default=False)
    is_buyer = models.BooleanField(_("Is Buyer"), default=False)

    phone = models.CharField(_("Phone Number"), max_length=20,default='')
    otp = models.CharField(max_length=6 , null=True , blank=True)
    shipping_address = models.ForeignKey(
        Address,
        related_name="user_shipping",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Shipping Address"),
    )

    billing_address = models.ForeignKey(
        Address,
        related_name="user_billing",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Billing Address"),
    )

    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name='subordinates')

    created = models.DateTimeField(_("Added On"), auto_now_add=True)
    updated = models.DateTimeField(_("Edited On"), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        ordering=['-created']

    def __str__(self):
        return self.email


from product.models import Product
class BuyerProfile(models.Model):
    user = models.OneToOneField(User, related_name="buyer_profile", on_delete=models.CASCADE)
    bank_account = models.CharField(_("Bank account"), max_length=50,null=True,blank=True)
    instapay_account = models.CharField(_("Instapay account"), max_length=50,null=True,blank=True)
    electronic_wallet = models.CharField(_("Electronic wallet"), max_length=50,null=True,blank=True)
    profile_picture = models.ImageField(
        _("Profile Picture"),
        upload_to=buyers_profile_pictures_path,
        validators=[image_extension_validator],
        null=True,
        blank=True,
    )
    favorite_products = models.ManyToManyField(Product, through='Favorite', related_name='favorited_by')


    def __str__(self):
        return self.user.email



class Favorite(models.Model):
    user_profile = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_profile', 'product')


class SupplierDocuments (models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='supplier_documents', null=True, blank=True)
    front_id=models.FileField(_("Front side of ID"),upload_to=suppliers_documents_path)
    back_id=models.FileField(_("Back side of ID"),upload_to=suppliers_documents_path)
    tax_card=models.FileField(_("Tax card"),upload_to=suppliers_documents_path)
    commercial_record=models.FileField(_("Commercial Record"),upload_to=suppliers_documents_path)
    bank_statement=models.FileField(_("Bank statement"),upload_to=suppliers_documents_path)
    def __str__(self) -> str:
        return self.user.email


class SupplierProfile(models.Model):
    user = models.OneToOneField(User, related_name="supplier_profile", on_delete=models.CASCADE)
    entity_address= models.ForeignKey(Address,related_name="entity_address",on_delete=models.SET_NULL,null=True)
    bank_account = models.CharField(_("Bank account"), max_length=50,null=True,blank=True)
    instapay_account = models.CharField(_("Instapay account"), max_length=50,null=True,blank=True)
    electronic_wallet = models.CharField(_("Electronic wallet"), max_length=50,null=True,blank=True)
    documents = models.OneToOneField(SupplierDocuments, related_name="supplier_documents", on_delete=models.CASCADE)

    profile_picture = models.ImageField(
        _("Profile Picture"),
        upload_to=suppliers_profile_pictures_path,
        validators=[image_extension_validator],
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.user.email

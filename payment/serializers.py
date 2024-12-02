from rest_framework import serializers
from .models import Payment
from django.core.exceptions import ValidationError 

class Paymentserializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields='__all__'
    def validate_pay_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        if len(value) > 11:
            raise serializers.ValidationError("Phone number can not be more than 11 digits.")
        valid_phone=['010','011','012','015']
        if not any(value.startswith(prefix)for prefix in valid_phone):
            raise serializers.ValidationError("phone number must start with one of the following: 010,011,012,015")
        return value
    def validate(self, value):
        method = value.get('method')
        screenshot = value.get('screenshot')
        if method in ['INSTAPAY', 'VODAFONE_CASH'] and not screenshot:
            raise serializers.ValidationError({
                'screenshot': "Screenshot for your payment is required."
            })
        return value

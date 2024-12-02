from django.shortcuts import render
from .serializers import Paymentserializer
from .models import Payment
from order.models import  Order
from rest_framework import generics,status
from django.utils import timezone
from rest_framework.response import Response



class OrderpayInstapay(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = Paymentserializer
    def create(self, request, *args, **kwargs):
        # Deserialize the data with the Payment serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save the Payment instance
        payment = serializer.save()

        # Access the related Order and update fields
        order = payment.order
        if order.is_paid:
            order.cart.checked_out = True
            order.cart.save()
        else:
            return Response(
                {'error': 'Payment must be completed before checkout.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.payment_method = payment.method  # Use the method from the Payment
        order.paid_date = timezone.now()  # Set the paid date to current time
        order.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


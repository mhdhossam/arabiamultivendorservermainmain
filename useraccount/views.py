import json
import jwt
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _
from rest_framework import status , viewsets,mixins
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    ListAPIView,
    UpdateAPIView,
    DestroyAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
# from stats.models import Stats
# from .mixins import CheckBuyerAdminGroupMixin, CheckSupplierAdminGroupMixin
from .models import BuyerProfile, SupplierProfile, User,SupplierDocuments,Favorite
from product.models import Product
from product.serializers import ProductSerializer
from .serializers import (
    AddressSerializer,
    CustomTokenObtainPairSerializer,
    # StatsSerializer,
    UserSerializer,
    SupplierRegistrationSerializer,
    SupplierDocumentsSerializer,
    ResetPasswordWithOTPSerializer,
    RequestotpSerializer,
    VerfiyEmailserializer,
    ResetPasswordSerializer,
    FavoriteSerializer,
)
from .utils import send_temporary_password
import random
import string
from django.http import JsonResponse
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser , FormParser
from drf_yasg import openapi
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        if 'email' in request.data:
            request.data['email'] = request.data['email'].lower()
        # Check if the email is associated with an active account
        try:
            email = request.data.get('email')
            user = User.objects.get(email=email)

            # If the user is a buyer and the account is not active, send OTP
            if not user.is_active and not user.is_supplier:
                # Generate OTP
                new_otp = ''.join(random.choices(string.digits, k=6))
                user.otp = new_otp
                user.save()

                # Send OTP to the user's email
                send_temporary_password(
                    new_otp,
                    "emails/temp_password.html",
                    _("Arbia Account Activation"),
                    email,
                )

                # Inform the user to verify their account
                return JsonResponse({
                    'message': 'Your account is not verified. An OTP has been sent to your email to verify your account.',
                    'email': email
                }, status=403)

            # If the user is a supplier and the account is not active, inform them of verification pending
            elif not user.is_active and user.is_supplier:
                return JsonResponse({
                    'message': 'Your vendor account is not verified yet. Please wait while we review your documents for verification.'
                }, status=403)

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)

        try:
            response = super().post(request, *args, **kwargs)
            response_data = response.data
            token = response_data.get('access')
            refresh_token = response_data.get('refresh')
            # Set cookies for tokens
            response.set_cookie('access_token', token, httponly=True, secure=True, samesite='Lax')
            response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Lax')
            # Return original response data
            response = JsonResponse({'done successfully': 'done successfully', 'tokens':response_data})
            return response
        except AuthenticationFailed:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
        except (InvalidToken, TokenError) as e:
            # Handle invalid token errors
            return JsonResponse({'error': str(e)}, status=401)


class BuyerRegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['email'] = data.get('email', '').lower()
        serializer = self.get_serializer(data=data)
        # Validate the serializer
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
        password1 = data.get('password1')
        
        user = serializer.save(
            is_buyer=True,
            is_supplier=False,
            is_active=False, 
        )
        user.set_password(password1)
        user.save()

        BuyerProfile.objects.create(user=user)
        temp_password = ''.join(random.choices(string.digits, k=6))
        user.otp = temp_password 
        user.save() 
        email = user.email
        send_temporary_password(
            temp_password,
            "emails/temp_password.html",
            _("Arbia Account Activation"),
            email,
        )
        return Response({
            'message': 'A temporary password has been sent to your email address.',
            'email': email
        }, status=status.HTTP_201_CREATED)


class VerifyOTPView(GenericAPIView):
    serializer_class= VerfiyEmailserializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user.otp == otp:
            user.is_active = True  
            user.otp = None  # Clear the OTP after verification
            user.save()
            return Response({'message': 'Email successfully activated.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)


class RequestOTPview(GenericAPIView):
    serializer_class=RequestotpSerializer
    def post(self , request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        email = serializer.validated_data['email'].lower()
        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        new_otp = ''.join(random.choices(string.digits, k=6))
        user.otp = new_otp 
        user.save()
        request.session['reset_email'] = email 
        send_temporary_password(
                new_otp,
                "emails/temp_password.html",
                _("Arbia Account Activation"),
                email,
            )
        return Response({
            'message': 'A new OTP has been sent to your email address.',
            'email': email
        }, status=status.HTTP_200_OK)


class ResetPasswordWithOTPview(GenericAPIView):
    serializer_class = ResetPasswordWithOTPSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        otp=serializer.validated_data['otp']
        email=request.session.get('reset_email')
        if not email:
            return Response({'message': 'Session expired. Please request a new OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if user.otp == otp:
            request.session['otp_verified']=True
            return  Response({'message': 'OTP verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(GenericAPIView):
    serializer_class=ResetPasswordSerializer
    def post(self, request):
        if not request.session.get('otp_verified'):
            return Response({'message': 'OTP not verified. Please verify the OTP first.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password=serializer.validated_data['new_password']
        email=request.session.get('reset_email')
        if not email:
            return Response({'message': 'Session expired. Please request a new OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        user.set_password(new_password)
        user.otp=None
        user.save()

        request.session.pop('reset_email',None)
        request.session.pop('otp_verified',None)
        return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)


class SupplierRegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SupplierRegistrationSerializer
    parser_classes = (MultiPartParser , FormParser)
    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []

        return super().get_parsers()
    @swagger_auto_schema(
        request_body=SupplierRegistrationSerializer,
        responses={
            201: openapi.Response("User created", SupplierRegistrationSerializer),
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        data = request.data
        files=request.FILES
        print(data)
        # Manually extracting flattened user data
        user_data = {
            "email": data.get('user[email]'),
            "full_name": data.get('user[full_name]'),
            "password1": data.get('user[password1]'),
            "password2": data.get('user[password2]'),
            "phone": data.get('user[phone]'),
        }

        # Extract address data
        address_data = {
            "country": data.get('address[country]'),
            "state": data.get('address[state]'),
            "city": data.get('address[city]'),
            "postal_code": data.get('address[postal_code]'),
            "address_1": data.get('address[address_1]'),
            "address_2": data.get('address[address_2]'),
        }

        # Extract documents files
        documents_data = {
            "front_id": files.get('documents[front_id]'),
            "back_id": files.get('documents[back_id]'),
            "tax_card": files.get('documents[tax_card]'),
            "commercial_record": files.get('documents[commercial_record]'),
            "bank_statement": files.get('documents[bank_statement]'),
        }
        for key, file in documents_data.items():
            if not file or file.size == 0:
                return Response({"documents": f"{key} is missing or empty."}, status=status.HTTP_400_BAD_REQUEST)
        # Check for required fields
        if not user_data['email']:
            print(user_data)
            return Response({"user": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not documents_data:
            return Response({"documents": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not address_data['country']:
            return Response({"address": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate all serializers before saving
        user_serializer = UserSerializer(data=user_data)
        documents_serializer = SupplierDocumentsSerializer(data=documents_data)
        address_serializer = AddressSerializer(data=address_data)
        # Call is_valid on each serializer
        is_user_valid = user_serializer.is_valid()
        is_address_valid = address_serializer.is_valid()
        is_documents_valid = documents_serializer.is_valid()

        if is_user_valid and is_address_valid and is_documents_valid:
            try:
                with transaction.atomic():
                    # Save Address
                    address = address_serializer.save()

                    # Save User
                    user = user_serializer.save(
                        is_buyer=False, 
                        is_supplier=True,
                        is_active=False
                    )

                    # Save Supplier Documents
                    documents = documents_serializer.save(user=user)

                    # Save Supplier Profile
                    SupplierProfile.objects.create(
                        user=user,
                        documents=documents,
                        entity_address=address
                    )

                    return Response({"message": "Supplier registered successfully!"}, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Return all errors for invalid serializers
            return Response({
                "user_errors": user_serializer.errors,
                "documents_errors": documents_serializer.errors,
                "address_errors": address_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class=UserSerializer


class UserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # def perform_update(self, serializer):
    #     serializer.save()
    # def perform_destroy(self, instance):
    #     instance.delete()


class FavoriteViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Favorite.objects.none()
        user_profile = self.request.user.buyer_profile
        return Favorite.objects.filter(user_profile=user_profile).select_related('product').only('product__name', 'product__price')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_profile = request.user.buyer_profile
        cache_key = f'favorite_products_{user_profile.id}'
        cache.delete(cache_key)
        # Fetch the updated list of favorite products and set the cache again
        favorite_product_ids = user_profile.favorite_products.values_list('id', flat=True)
        products = Product.objects.filter(id__in=favorite_product_ids)\
            .select_related('category', 'brand')\
            .prefetch_related('images')\
            .annotate(average_rating=Avg('reviews__rating'))

        serializer = ProductSerializer(products, many=True)
        cache.set(cache_key, serializer.data, timeout=300)
        response_data = {
            'message': 'Product added to favorites successfully',
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user_profile = request.user.buyer_profile
        product_id = kwargs.get('pk')
        try:
            favorite = Favorite.objects.get(user_profile=user_profile, product_id=product_id)
            favorite.delete()
            cache_key = f'favorite_products_{user_profile.id}'
            cache.delete(cache_key)
            # Fetch the updated favorite products and store in the cache
            favorite_product_ids = user_profile.favorite_products.values_list('id', flat=True)
            products = Product.objects.filter(id__in=favorite_product_ids)\
                .select_related('category', 'brand')\
                .prefetch_related('images')\
                .annotate(average_rating=Avg('reviews__rating'))

            serializer = ProductSerializer(products, many=True)
            cache.set(cache_key, serializer.data, timeout=300)
            response_data = {
            'message': 'Product deleted successfully',
            }
            return Response(response_data,status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response({'detail': 'Favorite not found.'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['get'], url_path='products')
    def favorite_products(self, request):
        user_profile = request.user.buyer_profile
        cache_key = f'favorite_products_{user_profile.id}'
        cached_products = cache.get(cache_key)

        if cached_products is None:
            favorite_product_ids = user_profile.favorite_products.values_list('id', flat=True)
            products = Product.objects.filter(id__in=favorite_product_ids)\
            .select_related('category', 'brand')\
            .prefetch_related('images')\
            .annotate(average_rating=Avg('reviews__rating'))

            serializer = ProductSerializer(products, many=True)
            cached_products = serializer.data
            cache.set(cache_key, cached_products, timeout=300)  

        return Response(cached_products, status=status.HTTP_200_OK)

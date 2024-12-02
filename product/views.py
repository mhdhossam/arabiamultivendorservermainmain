# from advertisement.models import Advertisement
# from advertisement.serializers import AdvertisementSerializer
# from common.utils.create_slug import create_slug
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.db.models import Case, ExpressionWrapper, F, FloatField, Sum, When
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
# from openpyxl import load_workbook
from rest_framework import filters, status, viewsets,permissions
from rest_framework.generics import (
    DestroyAPIView,
    GenericAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet
from rest_framework.response import Response
from .filters import ProductFilter
from .mixins import CheckProductManagerGroupMixin, CheckSupplierAdminGroupMixin
from .models import Brand,Category,Product,Review,ProductFact,CategoryDimension,Size,Color
from .pagination import ProductPagination
from .filters import ProductFilter
from .permissions import IsVendor 
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductSerializer,
    ReviewSerializer,
    ProductFactSerializer,
    CategoryDimensionSerializer,
    SizeSerializer,
    ColorSerializer,
)
from django.http import Http404
from rest_framework.decorators import action
from django.utils.translation import activate
activate('en')


class CategoryViewSet(viewsets.ViewSet):
    queryset = Category.objects.all()
    
    def list(self, request):
        featured = request.GET.get("featured")
        parent_slug = request.GET.get("parent")
        if featured == "true":
            queryset = self.queryset.filter(is_featured=True)
        else:
            try:
                queryset = self.queryset.all()
                if parent_slug:
                    queryset = self.queryset.filter(parent__slug=parent_slug)
            except Category.DoesNotExist:
                raise Http404 ('Category not found.')
        serializer = CategorySerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class BrandViewSet( viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # limit = int(request.GET.get("limit")) if request.GET.get("limit") else None
        # if limit:
        #     queryset = queryset[:limit]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SizeViewSet(ReadOnlyModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer


class ColorViewSet(ReadOnlyModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class ProductViewSet( viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ["created","name",]
    # ordering = "name"
    pagination_class = ProductPagination
    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsVendor]
        else:
            self.permission_classes = [permissions.IsAuthenticatedOrReadOnly] 
        return super().get_permissions()
    def get_queryset(self):
        queryset = super().get_queryset().select_related('category', 'brand').prefetch_related('color', 'size')
        queryset = queryset.filter(is_available=True, stock_quantity__gt=0)
        category_slug = self.request.GET.get("category")
        if category_slug:
            try:

                category=Category.objects.get(slug=category_slug)
                descendant_categories=category.get_descendants(include_self=False)
                queryset=queryset.filter(category__in=descendant_categories)
            except Category.DoesNotExist:
                    raise Http404 ('Category not found.')
        return queryset

    @action(detail=False, methods=["get"])
    def cached_products(self, queryset_key):
        cache_key = f'query_{queryset_key}'
        queryset = cache.get(cache_key)
        if not queryset:
            queryset = Product.objects.filter(is_available=True, stock_quantity__gt=0).select_related('category', 'brand')
            cache.set(cache_key, queryset, timeout=900) 
        return queryset

    @action(detail=True, methods=["get"])
    def you_may_like(self, request, pk=None):
        try:
            product = self.get_object()
            recommended_by_category = Product.objects.filter(
                category=product.category
            ).exclude(sku=product.sku).filter(is_available=True).order_by('-total_views')[:5]

            recommended_by_brand = Product.objects.filter(
                brand=product.brand
            ).exclude(sku=product.sku).filter(is_available=True).order_by('-total_views')[:5]

            recommended_products = (recommended_by_category | recommended_by_brand).distinct()[:5]

            serializer = ProductSerializer(recommended_products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Product.DoesNotExist:
            raise Http404('Product not found.')
    @action(detail=False, methods=["get"], url_path="bycategory")
    def get_products_by_category(self, request):
        category_slug = request.query_params.get("category")
        print("category_slug",category_slug)
        if category_slug:
            try:
                cache_key = f'products_by_category_{category_slug}'
                cached_data = cache.get(cache_key)
                if cached_data:
                    return Response(cached_data, status=status.HTTP_200_OK)
                category = Category.objects.get(slug=category_slug)
                # Get all descendant categories of the specified category
                descendant_categories = category.get_descendants(include_self=True)
                # Filter products within these categories
                products = Product.objects.filter(category__in=descendant_categories).order_by('id') \
                .select_related('category', 'brand') \
                .prefetch_related('color', 'size')
                page = self.paginate_queryset(products)
                if page is not None:
                    serializer = ProductSerializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                serializer = ProductSerializer(products, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Category.DoesNotExist:
                return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Category slug is required."}, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Automatically assign the user and product when creating a review
        serializer.save(user=self.request.user)


class ProductRetrievalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductFact.objects.all()
    serializer_class = ProductFactSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["sales", "total_views"]


class VendorProductsViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Filter products by the logged-in user (supplier)
        queryset = Product.objects.filter(supplier=request.user)
        if not queryset.exists():  # Check if the queryset is empty
            return Response({"message": "You don't have any products yet."}, status=200)
        
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)


class CategoryRetrievalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CategoryDimension.objects.all()
    serializer_class = CategoryDimensionSerializer
    filter_backends = [DjangoFilterBackend]
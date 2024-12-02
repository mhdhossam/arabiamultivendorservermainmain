from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "product"

router = DefaultRouter()
router.register(r'reviews', views.ReviewViewSet)
router.register(r'productsretrieve', views.ProductRetrievalViewSet)
router.register(r'vendorproduct', views.VendorProductsViewSet, basename='vendorproduct')
router.register(r'categoryretrive', views.CategoryRetrievalViewSet)
router.register(r"category", views.CategoryViewSet)
router.register(r"brand", views.BrandViewSet)
router.register(r"size", views.SizeViewSet)
router.register(r"color", views.ColorViewSet)
router.register(r"", views.ProductViewSet)
urlpatterns = [
    path("", include(router.urls)),
    # path("delete", views.DeleteProductView.as_view()),
    # path("product/by-supplier/<id>/", views.GetSupplierProductsView.as_view()),

]

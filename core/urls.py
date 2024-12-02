from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path,re_path
from django.conf.urls.i18n import i18n_patterns
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.urls import re_path

schema_view = get_schema_view(
    openapi.Info(
        title="API DOCS",
        default_version='v1',
        description="Arabia API V1",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = i18n_patterns(
    path("api/admin/", admin.site.urls),
#==================================================
    #swagger doc
    #============
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
#====================================================
    path('rosetta/', include('rosetta.urls')),
    path('accounts/', include('allauth.urls')), #for  social login
    path("api/account/", include("useraccount.urls", namespace="account")),
    path("api/products/", include("product.urls", namespace="products")),
    path("api/advertisement/", include("advertisement.urls", namespace="advertisement")),
    path("api/order/", include("order.urls", namespace="order")),
    path("api/payment/", include("payment.urls", namespace="payment")),
    path("api/dashboard/", include("dashboard.urls", namespace="dashboard")),
    # path("api/contact/", include("contact.urls", namespace="contact")),
    # path("api/quote/", include("quote.urls", namespace="quote")),
    # path("api/wishlist/", include("wishlist.urls", namespace="wishlist")),
    # path("api/opportunity/", include("opportunity.urls", namespace="opportunity")),
    # path("api/chat/", include("chat.urls", namespace="chat")),
    # path("api/stats/", include("stats.urls", namespace="stats")),
    # path("api/company/", include("company.urls", namespace="company")),
    # path("api/wallet/", include("wallet.urls", namespace="wallet")),

)
urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


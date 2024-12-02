from django.urls import path,include
from rest_framework_simplejwt.views import TokenRefreshView
from dj_rest_auth.views import  LogoutView
from . import views
from rest_framework.routers import DefaultRouter
from .views import FavoriteViewSet

app_name = "account"

router = DefaultRouter()
router.register(r'favorites', FavoriteViewSet, basename='favorite')
urlpatterns = router.urls

urlpatterns = [
    path('', include(router.urls)),
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("buyer/register/", views.BuyerRegisterView.as_view(), name="buyer-register"),
    path("supplier/register/", views.SupplierRegisterView.as_view(), name="supplier-register"),
    path('verify-otp/',  views.VerifyOTPView.as_view(), name='verify-otp'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('passwordresetotp/',views.RequestOTPview.as_view(),name='requestOTP'),
    path('passwordresetotpverfiy/',views.ResetPasswordWithOTPview.as_view(),name='resetpassword'),
    path('passwordresetconfirm/',views.ResetPasswordView.as_view(),name='resetpassword'),
    path('users/',views.UserListView.as_view(), name='users-list'),
    path('users/<uuid:pk>/',views.UserDetailView.as_view(), name='users-detail'),
    # path('favorites/add/', views.FavoriteViewSet.as_view({'post': 'create'}), name='add-favorite'),
    # path("supplier/list/", views.SupplierListView.as_view(), name="supplier-list"),
    # path(
    #     "buyer/email-verify-refresh/",
    #     views.RefreshBuyerActivationLink.as_view(),
    #     name="activate-refresh",
    # ),
    # path("show_user_stats/", views.ShowUserStatsView.as_view()),
    # path("profile/", views.ProfileView.as_view(), name="profile"),
    # path("profile/<id>/", views.GetProfileView.as_view()),
    # path("update-password/", views.UpdatePasswordAPIView.as_view(), name="update-password"),
    # path(
    #     "supplier/employee/",
    #     views.SupplierEmployeeView.as_view(),
    #     name="supplier_employee",
    # ),
    # path(
    #     "buyer/employee/",
    #     views.BuyerEmployeeView.as_view(),
    #     name="buyer_employee",
    # ),
]

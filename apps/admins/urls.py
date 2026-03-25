from django.urls import path, include
from rest_framework. routers import DefaultRouter
from . views import (
    admin_login,
    AdminProfileView,
    AdminPasswordChangeView,
    PasswordResetRequestView,
    password_reset_validate,  # ✅ NEW
    password_reset_confirm,    # ✅ NEW
    DashboardViewSet,
    AdminViewSet,
)

router = DefaultRouter()
router.register(r'dashboard', DashboardViewSet, basename='admin-dashboard')
router.register(r'admins', AdminViewSet, basename='admin')

urlpatterns = [
    # Authentication
    path('login/', admin_login, name='admin-login'),
    path('profile/', AdminProfileView.as_view(), name='admin-profile'),
    path('password-change/', AdminPasswordChangeView.as_view(), name='admin-password-change'),
    
    # Password Reset
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/validate/', password_reset_validate, name='password-reset-validate'),  # ✅ NEW
    path('password-reset/confirm/', password_reset_confirm, name='password-reset-confirm'),      # ✅ NEW
    
    # Router URLs
    path('', include(router.urls)),
]
"""admin_panel/api/urls.py – All admin + auth endpoints."""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from admin_panel.api.views import (
    RegisterView, LoginView, LogoutView, ProfileView,
    ForgotPasswordView, ResetPasswordView,
    AdminDashboardView,
    UserListView, UserCreateView, UserDetailView, ToggleUserActiveView,
    AdminTaskListCreateView, AdminTaskDetailView,
    BusinessSettingsView,
    AdminReportView, TransactionListView, TransactionApproveView,
)

# Auth endpoints  /api/v1/auth/
auth_urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', ProfileView.as_view(), name='auth-profile'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='auth-forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='auth-reset-password'),
]

# Admin endpoints  /api/v1/admin/
admin_urlpatterns = [
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('users/', UserListView.as_view(), name='admin-user-list'),
    path('users/create/', UserCreateView.as_view(), name='admin-user-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='admin-user-detail'),
    path('users/<int:pk>/toggle-active/', ToggleUserActiveView.as_view(), name='admin-user-toggle'),
    path('tasks/', AdminTaskListCreateView.as_view(), name='admin-task-list'),
    path('tasks/<int:pk>/', AdminTaskDetailView.as_view(), name='admin-task-detail'),
    path('settings/', BusinessSettingsView.as_view(), name='admin-settings'),
    path('reports/', AdminReportView.as_view(), name='admin-reports'),
    path('transactions/', TransactionListView.as_view(), name='admin-transactions'),
    path('transactions/<int:pk>/approve/', TransactionApproveView.as_view(), name='admin-transaction-approve'),
]

# Unified urlpatterns
urlpatterns = auth_urlpatterns + admin_urlpatterns

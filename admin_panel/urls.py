"""admin_panel/urls.py – Both frontend and API routes."""

from django.urls import path, include
from .views import AdminDashboardView, AdminUsersView, AdminTasksView, AdminReportsView, AdminSettingsView

urlpatterns = [
    # Frontend Pages
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('users/', AdminUsersView.as_view(), name='admin-users'),
    path('tasks/', AdminTasksView.as_view(), name='admin-tasks'),
    path('reports/', AdminReportsView.as_view(), name='admin-reports'),
    path('settings/', AdminSettingsView.as_view(), name='admin-settings'),

    # API endpoints (existing)
    path('api/v1/', include('admin_panel.api.urls')),
]

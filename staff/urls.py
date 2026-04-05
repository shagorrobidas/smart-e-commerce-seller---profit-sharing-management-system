"""staff/urls.py – Both frontend and API routes."""

from django.urls import path, include
from .views import (
    StaffDashboardView, StaffInventoryView, StaffOrdersView, 
    StaffTasksView, StaffMessagesView, StaffReportsView
)

urlpatterns = [
    # Frontend Pages
    path('dashboard/', StaffDashboardView.as_view(), name='staff-dashboard'),
    path('inventory/', StaffInventoryView.as_view(), name='staff-inventory'),
    path('orders/', StaffOrdersView.as_view(), name='staff-orders'),
    path('tasks/', StaffTasksView.as_view(), name='staff-tasks'),
    path('messages/', StaffMessagesView.as_view(), name='staff-messages'),
    path('reports/', StaffReportsView.as_view(), name='staff-reports'),

    # API endpoints
    path('api/v1/', include('staff.api.urls')),
]

"""staff/api/urls.py – All staff endpoints."""

from django.urls import path

from staff.api.views import (
    StaffDashboardView,
    StaffOrderListCreateView, StaffOrderDetailView,
    StaffExpenseListCreateView, StaffExpenseDetailView,
    InventoryListCreateView, InventoryDetailView,
    StaffTaskListView, StaffTaskUpdateView,
    MessageListView, MessageCreateView, MessageMarkReadView, UnreadCountView, MessageContactListView,
)

urlpatterns = [
    # Dashboard
    path('dashboard/', StaffDashboardView.as_view(), name='staff-api-dashboard'),

    # Orders / Sales
    path('orders/', StaffOrderListCreateView.as_view(), name='staff-order-list'),
    path('orders/<int:pk>/', StaffOrderDetailView.as_view(), name='staff-order-detail'),

    # Expenses
    path('expenses/', StaffExpenseListCreateView.as_view(), name='staff-expense-list'),
    path('expenses/<int:pk>/', StaffExpenseDetailView.as_view(), name='staff-expense-detail'),

    # Inventory
    path('inventory/', InventoryListCreateView.as_view(), name='staff-inventory-list'),
    path('inventory/<int:pk>/', InventoryDetailView.as_view(), name='staff-inventory-detail'),

    # Tasks
    path('tasks/', StaffTaskListView.as_view(), name='staff-task-list'),
    path('tasks/<int:pk>/', StaffTaskUpdateView.as_view(), name='staff-task-update'),

    # Messages
    path('messages/', MessageListView.as_view(), name='staff-message-list'),
    path('messages/send/', MessageCreateView.as_view(), name='staff-message-send'),
    path('messages/<int:pk>/read/', MessageMarkReadView.as_view(), name='staff-message-read'),
    path('messages/unread-count/', UnreadCountView.as_view(), name='staff-unread-count'),

    # User List for Messaging
    path('users/', MessageContactListView.as_view(), name='staff-user-list'),
]

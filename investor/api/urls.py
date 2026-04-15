"""investor/api/urls.py – All investor endpoints."""

from django.urls import path

from investor.api.views import (
    InvestorDashboardView,
    InvestmentListCreateView, InvestmentDetailView,
    InvestorReportView, InvestorAgreementView,
)
# Re-use shared messaging views (import directly to avoid circular imports)
from staff.api.views.message_views import (
    MessageListView, MessageCreateView,
    MessageMarkReadView, UnreadCountView, MessageContactListView,
)

urlpatterns = [
    path('dashboard/', InvestorDashboardView.as_view(), name='investor-dashboard'),
    path('investments/', InvestmentListCreateView.as_view(), name='investor-investment-list'),
    path('investments/<int:pk>/', InvestmentDetailView.as_view(), name='investor-investment-detail'),
    path('reports/', InvestorReportView.as_view(), name='investor-reports'),
    path('agreements/', InvestorAgreementView.as_view(), name='investor-agreements'),

    # Messaging (Investor → Admin only)
    path('messages/', MessageListView.as_view(), name='investor-message-list'),
    path('messages/send/', MessageCreateView.as_view(), name='investor-message-send'),
    path('messages/<int:pk>/read/', MessageMarkReadView.as_view(), name='investor-message-read'),
    path('messages/unread-count/', UnreadCountView.as_view(), name='investor-unread-count'),
    path('messages/users/', MessageContactListView.as_view(), name='investor-user-list'),
]

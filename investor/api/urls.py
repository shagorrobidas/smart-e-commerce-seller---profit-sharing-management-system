"""investor/api/urls.py – All investor endpoints."""

from django.urls import path

from investor.api.views import (
    InvestorDashboardView,
    InvestmentListCreateView, InvestmentDetailView,
    InvestorReportView, InvestorAgreementView,
)

urlpatterns = [
    path('dashboard/', InvestorDashboardView.as_view(), name='investor-dashboard'),
    path('investments/', InvestmentListCreateView.as_view(), name='investor-investment-list'),
    path('investments/<int:pk>/', InvestmentDetailView.as_view(), name='investor-investment-detail'),
    path('reports/', InvestorReportView.as_view(), name='investor-reports'),
    path('agreements/', InvestorAgreementView.as_view(), name='investor-agreements'),
]

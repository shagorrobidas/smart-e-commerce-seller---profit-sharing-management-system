"""investor/urls.py – Both frontend and API routes."""

from django.urls import path, include
from .views import InvestorDashboardView, InvestorAgreementsView, InvestorInvestView, InvestorReportsView

urlpatterns = [
    # Frontend Pages
    path('dashboard/', InvestorDashboardView.as_view(), name='investor-dashboard-page'),
    path('agreements/', InvestorAgreementsView.as_view(), name='investor-agreements-page'),
    path('invest/', InvestorInvestView.as_view(), name='investor-invest'),
    path('reports/', InvestorReportsView.as_view(), name='investor-reports-page'),

    # API endpoints
    path('api/v1/', include('investor.api.urls')),
]

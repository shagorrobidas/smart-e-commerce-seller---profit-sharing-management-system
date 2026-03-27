"""investment_views.py – Investor: submit and view investment proposals."""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.models import Investment
from api.permissions import IsInvestorRole
from investor.api.serializers.investment_serializers import (
    InvestmentSerializer, InvestmentCreateSerializer
)


class InvestmentListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/investor/investments/ – View history or submit new proposal."""
    permission_classes = [IsAuthenticated, IsInvestorRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InvestmentCreateSerializer
        return InvestmentSerializer

    def get_queryset(self):
        return Investment.objects.filter(
            investor=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(investor=self.request.user)


class InvestmentDetailView(generics.RetrieveAPIView):
    """GET /api/v1/investor/investments/<id>/ – View investment details."""
    permission_classes = [IsAuthenticated, IsInvestorRole]
    serializer_class = InvestmentSerializer

    def get_queryset(self):
        return Investment.objects.filter(investor=self.request.user)

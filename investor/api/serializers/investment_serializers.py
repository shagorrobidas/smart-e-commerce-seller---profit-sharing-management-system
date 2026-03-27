"""Investment serializers for investor views."""

from rest_framework import serializers
from api.models import Investment


class InvestmentSerializer(serializers.ModelSerializer):
    investor_name = serializers.CharField(source='investor.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.name', read_only=True, default=None)

    class Meta:
        model = Investment
        fields = [
            'id', 'investor', 'investor_name', 'amount', 'equity_percent',
            'notes', 'status', 'reviewed_by', 'reviewed_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'investor', 'status', 'reviewed_by', 'created_at', 'updated_at']


class InvestmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = ['amount', 'equity_percent', 'notes']

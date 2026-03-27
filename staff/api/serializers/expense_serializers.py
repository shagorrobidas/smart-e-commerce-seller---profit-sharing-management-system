"""Expense serializers for staff."""

from rest_framework import serializers
from api.models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.name', read_only=True, default=None)
    approved_by_name = serializers.CharField(source='approved_by.name', read_only=True, default=None)

    class Meta:
        model = Expense
        fields = [
            'id', 'description', 'category', 'amount', 'note',
            'attachment', 'submitted_by', 'submitted_by_name',
            'approved_by', 'approved_by_name', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'submitted_by', 'approved_by', 'status', 'created_at', 'updated_at']


class ExpenseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['description', 'category', 'amount', 'note', 'attachment']

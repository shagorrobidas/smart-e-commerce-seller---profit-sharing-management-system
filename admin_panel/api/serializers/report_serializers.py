"""Report and settings serializers."""

from rest_framework import serializers
from api.models import BusinessSettings, Transaction


class BusinessSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessSettings
        fields = ['id', 'business_name', 'currency', 'tax_rate', 'announcement', 'logo', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    from_user_name = serializers.CharField(source='from_user.name', read_only=True, default=None)
    to_user_name = serializers.CharField(source='to_user.name', read_only=True, default=None)

    class Meta:
        model = Transaction
        fields = [
            'id', 'type', 'amount', 'from_user', 'from_user_name',
            'to_user', 'to_user_name', 'note', 'status',
            'reference_order', 'reference_expense', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

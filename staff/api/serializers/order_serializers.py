"""Order/Sale serializers for staff."""

from rest_framework import serializers
from api.models import Order


class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, default=None)
    staff_name = serializers.CharField(source='staff.name', read_only=True, default=None)

    class Meta:
        model = Order
        fields = [
            'id', 'product', 'product_name', 'staff', 'staff_name',
            'quantity', 'amount', 'platform', 'note', 'attachment',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'staff', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['product', 'quantity', 'amount', 'platform', 'note', 'attachment']

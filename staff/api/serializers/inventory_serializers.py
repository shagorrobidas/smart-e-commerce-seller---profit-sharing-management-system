"""Inventory/Product serializers."""

from rest_framework import serializers
from api.models import Product


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    added_by_name = serializers.CharField(source='added_by.name', read_only=True, default=None)
    is_low_stock = serializers.BooleanField(read_only=True)
    profit_per_unit = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'stock', 'buy_price', 'sell_price', 'image',
            'added_by', 'added_by_name', 'is_low_stock',
            'profit_per_unit', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'added_by', 'created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'stock', 'buy_price', 'sell_price', 'image']

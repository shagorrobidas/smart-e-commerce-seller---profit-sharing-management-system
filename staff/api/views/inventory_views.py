"""inventory_views.py – Staff: manage product inventory."""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.models import Product, Category
from api.permissions import IsAdminOrStaff
from staff.api.serializers.inventory_serializers import ProductSerializer, ProductCreateSerializer, CategorySerializer

class CategoryListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/staff/categories/"""
    permission_classes = [IsAuthenticated, IsAdminOrStaff]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class InventoryListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/staff/inventory/ – List products or add new stock."""
    permission_classes = [IsAuthenticated, IsAdminOrStaff]
    queryset = Product.objects.select_related('category', 'added_by').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category')
        low_stock = self.request.query_params.get('low_stock')
        if search:
            qs = qs.filter(name__icontains=search)
        if category:
            qs = qs.filter(category__name=category)
        if low_stock == 'true':
            qs = qs.filter(stock__lte=10)
        return qs

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class InventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/staff/inventory/<id>/ – Manage product."""
    permission_classes = [IsAuthenticated, IsAdminOrStaff]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

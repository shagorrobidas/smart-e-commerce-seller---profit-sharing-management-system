"""order_views.py – Staff: record and view sales/orders."""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.models import Order, Product, Transaction
from api.permissions import IsStaffRole
from staff.api.serializers.order_serializers import OrderSerializer, OrderCreateSerializer


class StaffOrderListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/staff/orders/ – List own orders or record a new sale."""
    permission_classes = [IsAuthenticated, IsStaffRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        qs = Order.objects.filter(staff=self.request.user).select_related('product')
        status_filter = self.request.query_params.get('status')
        platform = self.request.query_params.get('platform')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if platform:
            qs = qs.filter(platform=platform)
        return qs

    def perform_create(self, serializer):
        order = serializer.save(staff=self.request.user)

        # Create transaction record for audit trail
        Transaction.objects.create(
            type='sale',
            amount=order.amount,
            from_user=None,
            to_user=self.request.user,
            note=f"Sale: {order.product.name if order.product else 'N/A'} on {order.platform}",
            status='approved',
            reference_order=order,
        )

        # Update product stock if product linked
        if order.product and order.quantity:
            product = order.product
            if product.stock >= order.quantity:
                product.stock -= order.quantity
                product.save()


class StaffOrderDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/staff/orders/<id>/ – View or update own order."""
    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(staff=self.request.user)

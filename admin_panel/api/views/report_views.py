"""report_views.py – Admin: full analytics and report generation."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from api.models import Order, Expense, Transaction, User, Product
from api.permissions import IsAdminRole


class AdminReportView(APIView):
    """GET /api/v1/admin/reports/ – Aggregated reports by period."""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        period = request.query_params.get('period', 'month')  # month, quarter, year, all

        if period == 'month':
            days = 30
        elif period == 'quarter':
            days = 90
        elif period == 'year':
            days = 365
        else:
            days = None

        order_qs = Order.objects.filter(status='completed')
        expense_qs = Expense.objects.filter(status='approved')

        if days:
            since = timezone.now() - timedelta(days=days)
            order_qs = order_qs.filter(created_at__gte=since)
            expense_qs = expense_qs.filter(created_at__gte=since)

        total_sales = order_qs.aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = expense_qs.aggregate(total=Sum('amount'))['total'] or 0
        net_profit = total_sales - total_expenses

        # Sales by platform
        sales_by_platform = list(
            order_qs.values('platform').annotate(
                total=Sum('amount'), count=Count('id')
            ).order_by('-total')
        )

        # Expenses by category
        expenses_by_category = list(
            expense_qs.values('category').annotate(
                total=Sum('amount'), count=Count('id')
            ).order_by('-total')
        )

        # Top selling products
        top_products = list(
            order_qs.exclude(product=None).values(
                'product__name'
            ).annotate(
                total_revenue=Sum('amount'), order_count=Count('id')
            ).order_by('-total_revenue')[:5]
        )

        # Staff performance
        staff_performance = list(
            order_qs.exclude(staff=None).values(
                'staff__name', 'staff__id'
            ).annotate(
                total_sales=Sum('amount'), order_count=Count('id')
            ).order_by('-total_sales')
        )

        # Inventory summary
        low_stock_count = Product.objects.filter(stock__lte=10).count()
        total_inventory_value = Product.objects.aggregate(
            val=Sum('sell_price')
        )['val'] or 0

        return Response({
            'period': period,
            'summary': {
                'total_sales': float(total_sales),
                'total_expenses': float(total_expenses),
                'net_profit': float(net_profit),
                'profit_margin': round(
                    float(net_profit / total_sales * 100) if total_sales else 0, 2
                ),
            },
            'sales_by_platform': [
                {**item, 'total': float(item['total'])} for item in sales_by_platform
            ],
            'expenses_by_category': [
                {**item, 'total': float(item['total'])} for item in expenses_by_category
            ],
            'top_products': [
                {**p, 'total_revenue': float(p['total_revenue'])} for p in top_products
            ],
            'staff_performance': [
                {**s, 'total_sales': float(s['total_sales'])} for s in staff_performance
            ],
            'inventory': {
                'low_stock_count': low_stock_count,
                'total_value': float(total_inventory_value),
            },
        })


class TransactionListView(APIView):
    """GET/PATCH /api/v1/admin/transactions/ – View & approve transactions."""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        transactions = Transaction.objects.select_related(
            'from_user', 'to_user'
        ).order_by('-created_at')[:50]
        data = [{
            'id': t.id,
            'type': t.type,
            'amount': float(t.amount),
            'from_user': t.from_user.name if t.from_user else None,
            'to_user': t.to_user.name if t.to_user else None,
            'note': t.note,
            'status': t.status,
            'date': t.created_at.strftime('%Y-%m-%d %H:%M'),
        } for t in transactions]
        return Response({'results': data, 'count': len(data)})


class TransactionApproveView(APIView):
    """PATCH /api/v1/admin/transactions/<id>/approve/"""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def patch(self, request, pk):
        try:
            txn = Transaction.objects.get(pk=pk)
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found.'}, status=404)

        action = request.data.get('action', 'approve')
        if action == 'approve':
            txn.status = 'approved'
            msg = 'Transaction approved.'
        elif action == 'reject':
            txn.status = 'rejected'
            msg = 'Transaction rejected.'
        else:
            return Response({'error': 'Invalid action. Use approve or reject.'}, status=400)

        txn.save()
        return Response({'message': msg, 'status': txn.status})

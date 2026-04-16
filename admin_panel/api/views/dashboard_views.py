"""dashboard_views.py – Admin business overview and analytics."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from api.models import Order, Expense, Transaction, User, Task, Investment
from api.permissions import IsAdminRole


class AdminDashboardView(APIView):
    """GET /api/v1/admin/dashboard/ – Full business stats for admin."""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        # Aggregate financial data
        total_sales = Order.objects.filter(
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_expenses = Expense.objects.filter(
            status='approved'
        ).aggregate(total=Sum('amount'))['total'] or 0

        net_profit = total_sales - total_expenses

        # User counts by role
        user_stats = User.objects.values('role').annotate(count=Count('id'))
        user_counts = {item['role']: item['count'] for item in user_stats}

        # Task stats
        task_stats = {
            'total': Task.objects.count(),
            'pending': Task.objects.filter(status='pending').count(),
            'in_progress': Task.objects.filter(status='in_progress').count(),
            'completed': Task.objects.filter(status='completed').count(),
        }

        # Investment stats
        total_invested = Investment.objects.filter(
            status='approved'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Monthly revenue trend (last 6 months)
        monthly_data = []
        for i in range(5, -1, -1):
            month_start = (timezone.now() - timedelta(days=30 * i)).replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            month_sales = Order.objects.filter(
                status='completed',
                created_at__gte=month_start,
                created_at__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            month_expenses = Expense.objects.filter(
                status='approved',
                created_at__gte=month_start,
                created_at__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            monthly_data.append({
                'month': month_start.strftime('%b %Y'),
                'sales': float(month_sales),
                'expenses': float(month_expenses),
                'profit': float(month_sales - month_expenses),
            })

        # Combined Recent activity (Orders + Expenses)
        recent_orders = Order.objects.select_related('staff', 'product').order_by('-created_at')[:10]
        recent_expenses = Expense.objects.select_related('submitted_by').order_by('-created_at')[:10]
        
        all_activity = []
        for o in recent_orders:
            all_activity.append({
                'id': f"order-{o.id}",
                'date': o.created_at.strftime('%Y-%m-%d %H:%M'),
                'sort_date': o.created_at,
                'type': 'sale',
                'description': f"Sale: {o.product.name if o.product else 'Unknown'} ({o.platform})",
                'amount': float(o.amount),
                'status': o.status,
                'by_name': o.staff.name if o.staff else 'Unknown',
            })
        
        for e in recent_expenses:
            all_activity.append({
                'id': f"expense-{e.id}",
                'date': e.created_at.strftime('%Y-%m-%d %H:%M'),
                'sort_date': e.created_at,
                'type': 'expense',
                'description': f"Expense: {e.description} ({e.category})",
                'amount': float(e.amount),
                'status': e.status,
                'by_name': e.submitted_by.name if e.submitted_by else 'Unknown',
            })
        
        # Sort combined and take top 10
        all_activity.sort(key=lambda x: x['sort_date'], reverse=True)
        recent_activity = all_activity[:10]

        # Pending Investments
        pending_investments = Investment.objects.filter(status='pending').select_related('investor')
        inv_data = [{
            'id': i.id,
            'investor_name': i.investor.name,
            'amount': float(i.amount),
            'equity': float(i.equity_percent) if i.equity_percent else 0,
            'date': i.created_at.strftime('%Y-%m-%d %H:%M'),
        } for i in pending_investments]

        return Response({
            'financials': {
                'total_sales': float(total_sales),
                'total_expenses': float(total_expenses),
                'net_profit': float(net_profit),
                'total_invested': float(total_invested),
            },
            'users': user_counts,
            'tasks': task_stats,
            'monthly_trend': monthly_data,
            'recent_activity': recent_activity,
            'pending_investments': inv_data,
        })

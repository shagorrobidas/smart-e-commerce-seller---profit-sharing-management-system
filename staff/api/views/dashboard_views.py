"""dashboard_views.py – Staff own performance dashboard."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from api.models import Order, Expense, Task
from api.permissions import IsStaffRole


class StaffDashboardView(APIView):
    """GET /api/v1/staff/dashboard/ – Staff's operational stats."""
    permission_classes = [IsAuthenticated, IsStaffRole]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        month_start = today.replace(day=1)

        # Today's sales
        today_sales = Order.objects.filter(
            staff=user, status='completed',
            created_at__date=today
        ).aggregate(total=Sum('amount'), count=Count('id'))

        # This month's sales
        month_sales = Order.objects.filter(
            staff=user, status='completed',
            created_at__date__gte=month_start
        ).aggregate(total=Sum('amount'), count=Count('id'))

        # Pending orders
        pending_orders = Order.objects.filter(
            staff=user, status='pending'
        ).count()

        # Task stats
        my_tasks = Task.objects.filter(assigned_to=user)
        task_stats = {
            'total': my_tasks.count(),
            'pending': my_tasks.filter(status='pending').count(),
            'in_progress': my_tasks.filter(status='in_progress').count(),
            'completed': my_tasks.filter(status='completed').count(),
        }

        # Monthly goal (50k target)
        monthly_target = 50000
        monthly_total = float(month_sales['total'] or 0)
        progress = round((monthly_total / monthly_target) * 100, 1) if monthly_target else 0

        # Weekly performance trend (last 7 days)
        weekly = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            day_total = Order.objects.filter(
                staff=user, status='completed', created_at__date=d
            ).aggregate(total=Sum('amount'))['total'] or 0
            weekly.append({
                'date': d.strftime('%a'),
                'amount': float(day_total)
            })

        return Response({
            'today': {
                'sales': float(today_sales['total'] or 0),
                'orders': today_sales['count'] or 0,
            },
            'month': {
                'sales': monthly_total,
                'orders': month_sales['count'] or 0,
                'target': monthly_target,
                'progress': min(progress, 100),
            },
            'pending_orders': pending_orders,
            'tasks': task_stats,
            'weekly_trend': weekly,
        })

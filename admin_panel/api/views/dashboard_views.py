"""dashboard_views.py – Admin business overview and analytics."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from api.models import Order, Expense, Transaction, User, Task, Investment, Product
from api.permissions import IsAdminRole


class AdminDashboardView(APIView):
    """GET /api/v1/admin/dashboard/ – Full business stats for admin."""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        # Filter by company if admin has one
        admin = request.user
        company_staff = User.objects.all()
        if admin.company:
            company_staff = company_staff.filter(company__iexact=admin.company.strip())
        
        # Aggregate financial data
        total_sales = Order.objects.filter(
            status='completed',
            staff__in=company_staff
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_expenses = Expense.objects.filter(
            status='approved',
            submitted_by__in=company_staff
        ).aggregate(total=Sum('amount'))['total'] or 0

        net_profit = total_sales - total_expenses

        # User counts by role (within same company)
        user_stats = company_staff.values('role').annotate(count=Count('id'))
        user_counts = {item['role']: item['count'] for item in user_stats}

        # Task stats (within same company)
        company_tasks = Task.objects.filter(assigned_to__in=company_staff)
        task_stats = {
            'total': company_tasks.count(),
            'pending': company_tasks.filter(status='pending').count(),
            'in_progress': company_tasks.filter(status='in_progress').count(),
            'completed': company_tasks.filter(status='completed').count(),
        }

        # Investment stats (within same company)
        total_invested = Investment.objects.filter(
            status='approved',
            investor__in=company_staff
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
                created_at__lt=month_end,
                staff__in=company_staff
            ).aggregate(total=Sum('amount'))['total'] or 0
            month_expenses = Expense.objects.filter(
                status='approved',
                created_at__gte=month_start,
                created_at__lt=month_end,
                submitted_by__in=company_staff
            ).aggregate(total=Sum('amount'))['total'] or 0
            monthly_data.append({
                'month': month_start.strftime('%b %Y'),
                'sales': float(month_sales),
                'expenses': float(month_expenses),
                'profit': float(month_sales - month_expenses),
            })

        # Combined Recent activity within same company
        recent_orders = Order.objects.select_related('staff', 'product').filter(
            staff__in=company_staff
        ).order_by('-created_at')[:10]
        
        recent_expenses = Expense.objects.select_related('submitted_by').filter(
            submitted_by__in=company_staff
        ).order_by('-created_at')[:10]

        recent_users = company_staff.order_by('-date_joined')[:10]
        
        recent_tasks = Task.objects.select_related('assigned_to').filter(
            assigned_to__in=company_staff
        ).order_by('-created_at')[:10]

        recent_investments = Investment.objects.select_related('investor').filter(
            investor__in=company_staff
        ).order_by('-created_at')[:10]

        recent_products = Product.objects.select_related('added_by').filter(
            added_by__in=company_staff
        ).order_by('-created_at')[:10]
        
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

        for u in recent_users:
            all_activity.append({
                'id': f"user-{u.id}",
                'date': u.date_joined.strftime('%Y-%m-%d %H:%M'),
                'sort_date': u.date_joined,
                'type': 'user',
                'description': f"New {u.role}: {u.name} joined",
                'amount': 0,
                'status': 'active' if u.is_active else 'inactive',
                'by_name': u.name,
            })

        for t in recent_tasks:
            all_activity.append({
                'id': f"task-{t.id}",
                'date': t.created_at.strftime('%Y-%m-%d %H:%M'),
                'sort_date': t.created_at,
                'type': 'task',
                'description': f"Task: {t.title} assigned to {t.assigned_to.name}",
                'amount': 0,
                'status': t.status,
                'by_name': t.assigned_by.name if t.assigned_by else 'Admin',
            })

        for i in recent_investments:
            all_activity.append({
                'id': f"invest-{i.id}",
                'date': i.created_at.strftime('%Y-%m-%d %H:%M'),
                'sort_date': i.created_at,
                'type': 'investment',
                'description': f"Investment Proposal: ৳{float(i.amount):.2f} from {i.investor.name}",
                'amount': float(i.amount),
                'status': i.status,
                'by_name': i.investor.name,
            })

        for p in recent_products:
            all_activity.append({
                'id': f"product-{p.id}",
                'date': p.created_at.strftime('%Y-%m-%d %H:%M'),
                'sort_date': p.created_at,
                'type': 'product',
                'description': f"Product Added: {p.name}",
                'amount': float(p.sell_price),
                'status': 'in_stock' if p.stock > 0 else 'out_of_stock',
                'by_name': p.added_by.name if p.added_by else 'Unknown',
            })
        
        # Sort combined and take top 15
        all_activity.sort(key=lambda x: x['sort_date'], reverse=True)
        recent_activity = all_activity[:15]

        # Pending Investments within same company
        pending_investments = Investment.objects.filter(
            status='pending',
            investor__in=company_staff
        ).select_related('investor')
        inv_data = [{
            'id': i.id,
            'investor_name': i.investor.name,
            'amount': float(i.amount),
            'equity': float(i.equity_percent) if i.equity_percent else 0,
            'date': i.created_at.strftime('%Y-%m-%d %H:%M'),
        } for i in pending_investments]

        # Pending Staff Approvals within same company
        pending_staff = company_staff.filter(role='staff', is_approved=False)
        staff_approvals = [{
            'id': s.id,
            'name': s.name,
            'email': s.email,
            'date': s.date_joined.strftime('%Y-%m-%d %H:%M'),
        } for s in pending_staff]

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
            'pending_staff': staff_approvals,
        })


class AdminProductListView(APIView):
    """GET /api/v1/admin/products/ – All products from the same company with uploader info."""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        admin = request.user

        # Base queryset: products added by users in the same company
        qs = Product.objects.select_related('category', 'added_by').all()

        if admin.company:
            # Filter products added by staff in the same company
            company_user_ids = User.objects.filter(
                company__iexact=admin.company.strip()
            ).values_list('id', flat=True)
            qs = qs.filter(added_by__id__in=company_user_ids)

        # Optional filters
        search = request.query_params.get('search', '').strip()
        category = request.query_params.get('category', '').strip()
        low_stock = request.query_params.get('low_stock', '').strip()
        added_by = request.query_params.get('added_by', '').strip()

        if search:
            qs = qs.filter(name__icontains=search)
        if category:
            qs = qs.filter(category__name__iexact=category)
        if low_stock == 'true':
            qs = qs.filter(stock__lte=10)
        if added_by:
            qs = qs.filter(added_by__id=added_by)

        qs = qs.order_by('-created_at')

        data = []
        for p in qs:
            data.append({
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'category': p.category.name if p.category else 'Uncategorized',
                'stock': p.stock,
                'buy_price': float(p.buy_price),
                'sell_price': float(p.sell_price),
                'profit_per_unit': float(p.profit_per_unit),
                'is_low_stock': p.is_low_stock,
                'image': request.build_absolute_uri(p.image.url) if p.image else None,
                'added_by': {
                    'id': p.added_by.id if p.added_by else None,
                    'name': p.added_by.name if p.added_by else 'Unknown',
                    'email': p.added_by.email if p.added_by else '',
                    'role': p.added_by.role if p.added_by else '',
                },
                'created_at': p.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': p.updated_at.strftime('%Y-%m-%d %H:%M'),
            })

        # Summary stats
        total = qs.count()
        low_stock_count = qs.filter(stock__lte=10).count()
        out_of_stock = qs.filter(stock=0).count()

        # Unique staff who added products
        staff_summary = list(
            qs.exclude(added_by=None)
            .values('added_by__id', 'added_by__name')
            .annotate(product_count=Count('id'))
            .order_by('-product_count')
        )

        return Response({
            'total': total,
            'low_stock_count': low_stock_count,
            'out_of_stock': out_of_stock,
            'staff_summary': [
                {
                    'id': s['added_by__id'],
                    'name': s['added_by__name'],
                    'product_count': s['product_count'],
                }
                for s in staff_summary
            ],
            'results': data,
        })


class AdminUserApproveView(APIView):
    """POST /api/v1/admin/users/<id>/approve/ – Approve a pending staff member."""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, pk):
        try:
            admin = request.user
            user_to_approve = User.objects.get(id=pk, role='staff')

            # Security check: must be same company
            if admin.company and user_to_approve.company.strip().lower() != admin.company.strip().lower():
                return Response({'error': 'Unauthorized: Different company'}, status=403)

            action = request.data.get('action', 'approve')
            if action == 'approve':
                user_to_approve.is_approved = True
                user_to_approve.save()
                return Response({'message': 'Staff approved successfully'})
            elif action == 'reject':
                user_to_approve.delete()  # Or set is_active=False
                return Response({'message': 'Staff request rejected'})
            
            return Response({'error': 'Invalid action'}, status=400)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

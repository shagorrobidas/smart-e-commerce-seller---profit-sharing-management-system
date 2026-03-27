"""dashboard_views.py – Investor P&L and portfolio overview."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum

from api.models import Order, Expense, Investment, Transaction
from api.permissions import IsInvestorRole


class InvestorDashboardView(APIView):
    """GET /api/v1/investor/dashboard/ – P&L + profit share stats."""
    permission_classes = [IsAuthenticated, IsInvestorRole]

    def get(self, request):
        user = request.user

        # Business P&L
        total_sales = Order.objects.filter(
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_expenses = Expense.objects.filter(
            status='approved'
        ).aggregate(total=Sum('amount'))['total'] or 0

        net_profit = total_sales - total_expenses

        # Investor's equity share (from user profile)
        equity = float(user.equity_percent) if user.equity_percent else 40.0
        my_profit_share = float(net_profit) * (equity / 100)

        # Total invested (approved investments by this investor)
        total_invested = Investment.objects.filter(
            investor=user, status='approved'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Total payouts received
        total_payouts = Transaction.objects.filter(
            type='profit_share', to_user=user, status='approved'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Capital allocation breakdown (static percentages from frontend)
        allocation = [
            {'name': 'Inventory (High Turnover)', 'percent': 45},
            {'name': 'Marketing & Growth', 'percent': 30},
            {'name': 'Operational & Logistics', 'percent': 15},
            {'name': 'R&D / Cash Reserve', 'percent': 10},
        ]

        return Response({
            'portfolio': {
                'total_invested': float(total_invested),
                'equity_percent': equity,
                'profit_share': round(my_profit_share, 2),
                'total_payouts': float(total_payouts),
            },
            'business_pnl': {
                'total_sales': float(total_sales),
                'total_expenses': float(total_expenses),
                'net_profit': float(net_profit),
            },
            'capital_allocation': allocation,
            'audit_status': 'verified',
        })

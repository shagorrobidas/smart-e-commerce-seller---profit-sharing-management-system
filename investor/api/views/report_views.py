"""report_views.py – Investor: financial reports and agreements."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from api.models import Order, Expense, Transaction, Investment
from api.permissions import IsInvestorRole


class InvestorReportView(APIView):
    """GET /api/v1/investor/reports/ – Financial reports for investor."""
    permission_classes = [IsAuthenticated, IsInvestorRole]

    def get(self, request):
        user = request.user
        equity = float(user.equity_percent) if user.equity_percent else 40.0

        # Monthly P&L overview (last 6 months)
        monthly = []
        for i in range(5, -1, -1):
            month_start = (timezone.now() - timedelta(days=30 * i)).replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            month_end = (month_start + timedelta(days=32)).replace(day=1)

            sales = Order.objects.filter(
                status='completed',
                created_at__gte=month_start, created_at__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0

            expenses = Expense.objects.filter(
                status='approved',
                created_at__gte=month_start, created_at__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0

            profit = float(sales) - float(expenses)
            my_share = profit * (equity / 100)

            monthly.append({
                'month': month_start.strftime('%b %Y'),
                'sales': float(sales),
                'expenses': float(expenses),
                'profit': profit,
                'my_share': round(my_share, 2),
            })

        # Investment history summary
        investment_summary = Investment.objects.filter(
            investor=user
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )

        # Payout history
        payouts = Transaction.objects.filter(
            type='profit_share', to_user=user, status='approved'
        ).order_by('-created_at')[:10]

        payout_list = [{
            'date': p.created_at.strftime('%Y-%m-%d'),
            'amount': float(p.amount),
            'note': p.note,
        } for p in payouts]

        return Response({
            'equity_percent': equity,
            'monthly_pnl': monthly,
            'investment_summary': {
                'total_invested': float(investment_summary['total'] or 0),
                'num_investments': investment_summary['count'] or 0,
            },
            'recent_payouts': payout_list,
        })


class InvestorAgreementView(APIView):
    """GET /api/v1/investor/agreements/ – View investment agreements."""
    permission_classes = [IsAuthenticated, IsInvestorRole]

    def get(self, request):
        user = request.user
        investments = Investment.objects.filter(investor=user).order_by('-created_at')

        agreements = [{
            'id': inv.id,
            'amount': float(inv.amount),
            'equity_percent': float(inv.equity_percent) if inv.equity_percent else None,
            'notes': inv.notes,
            'status': inv.status,
            'date': inv.created_at.strftime('%Y-%m-%d'),
            'reviewed_by': inv.reviewed_by.name if inv.reviewed_by else None,
        } for inv in investments]

        return Response({
            'agreements': agreements,
            'total': len(agreements),
        })

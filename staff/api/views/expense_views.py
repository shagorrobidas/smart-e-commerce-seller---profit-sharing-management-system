"""expense_views.py – Staff: submit and view expenses."""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.models import Expense, Transaction
from api.permissions import IsStaffRole
from staff.api.serializers.expense_serializers import ExpenseSerializer, ExpenseCreateSerializer


class StaffExpenseListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/staff/expenses/ – List own expenses or submit new."""
    permission_classes = [IsAuthenticated, IsStaffRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExpenseCreateSerializer
        return ExpenseSerializer

    def get_queryset(self):
        qs = Expense.objects.filter(submitted_by=self.request.user)
        status_filter = self.request.query_params.get('status')
        category = self.request.query_params.get('category')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if category:
            qs = qs.filter(category=category)
        return qs

    def perform_create(self, serializer):
        expense = serializer.save(submitted_by=self.request.user, status='pending')

        # Create pending transaction for admin approval
        Transaction.objects.create(
            type='expense',
            amount=expense.amount,
            from_user=self.request.user,
            to_user=None,
            note=f"Expense: {expense.description} ({expense.category})",
            status='pending',
            reference_expense=expense,
        )


class StaffExpenseDetailView(generics.RetrieveAPIView):
    """GET /api/v1/staff/expenses/<id>/ – View expense detail."""
    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        return Expense.objects.filter(submitted_by=self.request.user)

"""user_views.py – Admin user management (list, create, delete, update)."""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string

from api.models import User, Investment, Transaction
from api.permissions import IsAdminRole
from admin_panel.api.serializers.user_serializers import (
    UserListSerializer, UserCreateSerializer, UserProfileSerializer
)


def send_user_credentials_email(user, password):
    """Sends credential email to the newly created user."""
    subject = "Your SmartSeller Account Credentials"
    login_url = f"{settings.SITE_URL}/login/"
    message = (
        f"Hi {user.name},\n\n"
        f"An administrator has created an account for you at {settings.SITE_URL}.\n\n"
        f"Email: {user.email}\n"
        f"Password: {password}\n\n"
        f"You can log in here: {login_url}\n\n"
        f"Please change your password after logging in."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])



class UserListView(generics.ListAPIView):
    """GET /api/v1/admin/users/ – List users from the same company as the admin."""
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = UserListSerializer

    def get_queryset(self):
        admin = self.request.user
        # Base: exclude the requesting admin themselves; filter by same company
        qs = User.objects.all().order_by('-date_joined')
        if admin.company:
            qs = qs.filter(company=admin.company)

        role = self.request.query_params.get('role')
        search = self.request.query_params.get('search')
        if role:
            qs = qs.filter(role=role)
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(email__icontains=search)
        return qs


class UserCreateView(generics.CreateAPIView):
    """POST /api/v1/admin/users/create/ – Create a new user.
    Auto-assigns the admin's company if none provided."""
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = UserCreateSerializer

    def perform_create(self, serializer):
        admin = self.request.user
        # Generate random 10-character password
        password = get_random_string(10)
        # Strictly inherit admin's company if it exists
        company = admin.company if admin.company else serializer.validated_data.get('company', '')
        
        user = serializer.save(company=company, password=password)
        user.is_approved = True
        user.is_email_verified = True
        user.save()


        
        # Send credential email
        try:
            send_user_credentials_email(user, password)
        except Exception as e:
            # Log error or handle as needed; creation still succeeds
            print(f"Failed to send credential email: {e}")



class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/admin/users/<id>/ – Manage individual user."""
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        admin = self.request.user
        qs = User.objects.all()
        if admin.company:
            qs = qs.filter(company=admin.company)
        return qs

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response(
                {'error': 'You cannot delete your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.delete()
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class ToggleUserActiveView(APIView):
    """PATCH /api/v1/admin/users/<id>/toggle-active/ – Enable or disable user."""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def patch(self, request, pk):
        admin = request.user
        try:
            # Only allow toggling users in the same company
            qs = User.objects.all()
            if admin.company:
                qs = qs.filter(company=admin.company)
            user = qs.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user == request.user:
            return Response({'error': 'You cannot deactivate yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = not user.is_active
        user.save()
        return Response({
            'message': f"User {'activated' if user.is_active else 'deactivated'} successfully.",
            'is_active': user.is_active
        })


class InvestmentApprovalView(APIView):
    """PATCH /api/v1/admin/investments/<id>/approve/ – Approve/Reject investment proposals."""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def patch(self, request, pk):
        try:
            investment = Investment.objects.select_related('investor').get(pk=pk)
        except Investment.DoesNotExist:
            return Response({'error': 'Investment proposal not found.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action not in ['approve', 'reject']:
            return Response({'error': 'Invalid action. Use approve or reject.'}, status=status.HTTP_400_BAD_REQUEST)

        if investment.status != 'pending':
            return Response({'error': f"Investment is already {investment.status}."}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'approve':
            investment.status = 'approved'
            investment.reviewed_by = request.user
            
            # Logic: Update investor profile
            investor = investment.investor
            investor.balance += investment.amount
            if investment.equity_percent:
                investor.equity_percent += investment.equity_percent
            investor.save()

            # Create Audit Transaction
            Transaction.objects.create(
                type='investment',
                amount=investment.amount,
                to_user=investor,
                note=f"Injection Approval: {investment.equity_percent if investment.equity_percent else 0}% Equity stake added.",
                status='approved'
            )
            
            msg = "Investment proposal approved and capital credited."
        else:
            investment.status = 'rejected'
            investment.reviewed_by = request.user
            msg = "Investment proposal rejected."

        investment.save()
        return Response({'message': msg, 'status': investment.status})

"""user_views.py – Admin user management (list, create, delete, update)."""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.models import User
from api.permissions import IsAdminRole
from admin_panel.api.serializers.user_serializers import (
    UserListSerializer, UserCreateSerializer, UserProfileSerializer
)


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
        # Inherit admin's company if not explicitly set
        company = serializer.validated_data.get('company') or admin.company
        serializer.save(company=company)


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

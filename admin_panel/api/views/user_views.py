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
    """GET /api/v1/admin/users/ – List all system users."""
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = UserListSerializer
    queryset = User.objects.all().order_by('-date_joined')

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get('role')
        search = self.request.query_params.get('search')
        if role:
            qs = qs.filter(role=role)
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(email__icontains=search)
        return qs


class UserCreateView(generics.CreateAPIView):
    """POST /api/v1/admin/users/ – Create a new user."""
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = UserCreateSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/admin/users/<id>/ – Manage individual user."""
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()

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
        try:
            user = User.objects.get(pk=pk)
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

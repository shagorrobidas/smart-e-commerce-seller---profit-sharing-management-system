"""task_views.py – Staff: view and update assigned tasks."""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.models import Task
from api.permissions import IsStaffRole
from staff.api.serializers.task_serializers import StaffTaskSerializer


class StaffTaskListView(generics.ListAPIView):
    """GET /api/v1/staff/tasks/ – View my assigned tasks."""
    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = StaffTaskSerializer

    def get_queryset(self):
        qs = Task.objects.filter(
            assigned_to=self.request.user
        ).select_related('assigned_by')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class StaffTaskUpdateView(generics.UpdateAPIView):
    """PATCH /api/v1/staff/tasks/<id>/ – Update task status."""
    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = StaffTaskSerializer

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        # Staff can only update the status field
        allowed_statuses = ['pending', 'in_progress', 'completed']
        new_status = request.data.get('status')
        if new_status and new_status not in allowed_statuses:
            return Response(
                {'error': f"Status must be one of: {', '.join(allowed_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().partial_update(request, *args, **kwargs)

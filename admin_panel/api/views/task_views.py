"""task_views.py – Admin task management: assign, list, update."""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.models import Task, User
from api.permissions import IsAdminRole
from admin_panel.api.serializers.task_serializers import TaskSerializer, TaskCreateSerializer


class AdminTaskListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/admin/tasks/ – List all tasks or assign a new task."""
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Task.objects.select_related('assigned_to', 'assigned_by').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        staff_id = self.request.query_params.get('staff_id')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if staff_id:
            qs = qs.filter(assigned_to_id=staff_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class AdminTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/admin/tasks/<id>/"""
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

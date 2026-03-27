"""Staff-side task serializers (read + status update only)."""

from rest_framework import serializers
from api.models import Task


class StaffTaskSerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.CharField(source='assigned_by.name', read_only=True, default=None)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_by', 'assigned_by_name',
            'due_date', 'status', 'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'title', 'description', 'assigned_by',
            'due_date', 'created_at', 'updated_at'
        ]

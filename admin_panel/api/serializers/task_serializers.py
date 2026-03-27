"""Task serializers for admin task management."""

from rest_framework import serializers
from api.models import Task, User


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.name', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to', 'assigned_to_name',
            'assigned_by', 'assigned_by_name', 'due_date', 'status',
            'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'assigned_by', 'created_at', 'updated_at']


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date']

    def validate_assigned_to(self, value):
        if value.role != 'staff':
            raise serializers.ValidationError("Tasks can only be assigned to staff members.")
        return value

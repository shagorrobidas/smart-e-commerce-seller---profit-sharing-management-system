"""message_views.py – Staff: internal messaging."""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db import models as db_models
from api.models import Message, User
from api.permissions import IsStaffRole, IsAdminOrStaff
from admin_panel.api.serializers.user_serializers import UserListSerializer


class MessageSerializer:
    """Inline serializer for messages."""
    pass


from rest_framework import serializers


class MessageOutSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.name', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_name', 'receiver', 'receiver_name',
            'content', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'sender', 'created_at']


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['receiver', 'content']




class MessageListView(generics.ListAPIView):
    """GET /api/v1/staff/messages/ – List messages (sent + received)."""
    permission_classes = [IsAuthenticated]
    serializer_class = MessageOutSerializer

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            db_models.Q(sender=user) | db_models.Q(receiver=user)
        ).select_related('sender', 'receiver')


class MessageCreateView(generics.CreateAPIView):
    """POST /api/v1/staff/messages/ – Send a message."""
    permission_classes = [IsAuthenticated]
    serializer_class = MessageCreateSerializer

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class MessageMarkReadView(APIView):
    """PATCH /api/v1/staff/messages/<id>/read/ – Mark message as read."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            message = Message.objects.get(pk=pk, receiver=request.user)
        except Message.DoesNotExist:
            return Response({'error': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)

        message.is_read = True
        message.save()
        return Response({'message': 'Marked as read.'})


class UnreadCountView(APIView):
    """GET /api/v1/staff/messages/unread-count/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Message.objects.filter(receiver=request.user, is_read=False).count()
        return Response({'unread_count': count})
class StaffUserListView(generics.ListAPIView):
    """GET /api/v1/staff/users/ – List users for messaging (Staff/Admin)."""
    permission_classes = [IsAuthenticated, IsAdminOrStaff]
    serializer_class = UserListSerializer 
    queryset = User.objects.filter(role__in=['admin', 'staff']).exclude(is_active=False)

    def get_serializer_class(self):
        return UserListSerializer

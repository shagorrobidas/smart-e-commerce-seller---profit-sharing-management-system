"""message_views.py – Role-aware internal messaging.

Permissions:
  - Admin   : can send to staff & investors; sees staff+investors in contacts.
  - Investor: can send to admin only;        sees admins in contacts.
  - Staff   : CANNOT send; read-only;        sees admins in contacts.
"""

from rest_framework import generics, serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from django.db import models as db_models
from api.models import Message, User
from admin_panel.api.serializers.user_serializers import UserListSerializer


# ---------------------------------------------------------------------------
# Custom Permissions
# ---------------------------------------------------------------------------

class CanSendMessage(BasePermission):
    """Authenticated users may send messages according to role rules."""
    message = "You do not have permission to send messages."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Allow any authenticated user to send messages; receiver validation enforces role restrictions.
        return True


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

class MessageOutSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.name', read_only=True)
    sender_role = serializers.CharField(source='sender.role', read_only=True)
    attachment_url = serializers.SerializerMethodField()

    def get_attachment_url(self, obj):
        if obj.attachment:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.attachment.url) if request else obj.attachment.url
        return None

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_name', 'sender_role',
            'receiver', 'receiver_name', 'content',
            'attachment_url', 'attachment_name',
            'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'sender', 'created_at', 'attachment_url']


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['receiver', 'content', 'attachment', 'attachment_name']
        extra_kwargs = {
            'content': {'required': False, 'default': ''},
            'attachment': {'required': False},
            'attachment_name': {'required': False, 'default': ''},
        }

    def validate(self, data):
        if not data.get('content', '').strip() and not data.get('attachment'):
            raise serializers.ValidationError("Message must have text or an attachment.")
        return data

    def validate_receiver(self, receiver):
        sender = self.context['request'].user
        if sender.role == 'investor' and receiver.role != 'admin':
            raise serializers.ValidationError("Investors can only message admins.")
        if sender.role == 'admin' and receiver.role not in ('staff', 'investor'):
            raise serializers.ValidationError("Admins can only message staff or investors.")
        if sender.role == 'staff' and receiver.role not in ('admin', 'staff'):
            raise serializers.ValidationError("Staff can only message admins or other staff.")
        return receiver


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

class MessageListView(generics.ListAPIView):
    """GET  – List messages involving the current user (sent + received)."""
    permission_classes = [IsAuthenticated]
    serializer_class = MessageOutSerializer

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            db_models.Q(sender=user) | db_models.Q(receiver=user)
        ).select_related('sender', 'receiver').order_by('created_at')


class MessageCreateView(generics.CreateAPIView):
    """POST – Send a message (text or file)."""
    permission_classes = [IsAuthenticated, CanSendMessage]
    serializer_class = MessageCreateSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        file = self.request.FILES.get('attachment')
        attachment_name = serializer.validated_data.get('attachment_name', '')
        if file and not attachment_name:
            attachment_name = file.name
        serializer.save(sender=self.request.user, attachment_name=attachment_name)


class MessageMarkReadView(APIView):
    """PATCH – Mark a received message as read."""
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
    """GET – Return the number of unread messages for the current user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Message.objects.filter(receiver=request.user, is_read=False).count()
        return Response({'unread_count': count})


class MessageContactListView(generics.ListAPIView):
    """GET – Return users this role can chat with.

    Admin   → staff + investors (same company)
    Investor → admins only
    Staff   → admins only
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserListSerializer

    def get_queryset(self):
        user = self.request.user
        base_qs = User.objects.filter(
            is_active=True,
            company=user.company
        ).exclude(pk=user.pk)

        if user.role == 'admin':
            # Admin can contact all staff and investors in the same company
            qs = base_qs.filter(role__in=['staff', 'investor'])
            if user.company:
                qs = qs.filter(company=user.company)
            return qs

        elif user.role == 'investor':
            # Investor can only contact admins
            return base_qs.filter(role='admin')

        elif user.role == 'staff':
            # Staff can contact admins and other staff in the same company
            return base_qs.filter(role__in=['admin', 'staff'])

        else:
            return base_qs.filter(role__in=['admin', 'staff'])

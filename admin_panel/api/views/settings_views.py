"""settings_views.py – Business settings management (singleton)."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from api.models import BusinessSettings
from api.permissions import IsAdminRole
from admin_panel.api.serializers.report_serializers import BusinessSettingsSerializer


class BusinessSettingsView(APIView):
    """GET/PATCH /api/v1/admin/settings/ – Get or update business settings."""
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        settings = BusinessSettings.get_settings()
        serializer = BusinessSettingsSerializer(settings)
        return Response(serializer.data)

    def patch(self, request):
        settings = BusinessSettings.get_settings()
        serializer = BusinessSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Settings updated.', 'data': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

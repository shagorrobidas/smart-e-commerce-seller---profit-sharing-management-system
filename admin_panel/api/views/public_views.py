from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from api.models import Business, ContactMessage
from admin_panel.api.serializers.public_serializers import (
    BusinessRegistrationSerializer, ContactMessageSerializer
)

class BusinessRegistrationView(APIView):
    """POST /api/v1/public/business-register/ – Public business registration."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = BusinessRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            business = serializer.save()
            business.is_approved = False
            business.save()

            return Response({
                'message': 'Business registration submitted. We will contact you after review.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactMessageView(APIView):
    """POST /api/v1/public/contact/ – Public contact form."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Message sent successfully. We will get back to you soon.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

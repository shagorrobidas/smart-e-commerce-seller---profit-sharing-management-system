from rest_framework import generics
from rest_framework.permissions import AllowAny
from api.models import Business
from rest_framework import serializers

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name']

class BusinessListView(generics.ListAPIView):
    """Publicly accessible list of registered businesses for registration form."""
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [AllowAny]

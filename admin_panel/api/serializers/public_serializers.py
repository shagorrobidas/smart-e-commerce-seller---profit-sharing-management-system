from rest_framework import serializers
from api.models import Business, ContactMessage

class BusinessRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['name', 'owner_name', 'email', 'phone', 'description', 'address']

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

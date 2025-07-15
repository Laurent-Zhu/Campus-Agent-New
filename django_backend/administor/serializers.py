from rest_framework import serializers
from .models import Resource, Subject

class ResourceSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    uploader_name = serializers.CharField(source='uploader.username', read_only=True)

    class Meta:
        model = Resource
        fields = ['id', 'name', 'type', 'file', 'subject', 'subject_name', 'uploader', 'uploader_name', 'shared', 'create_at']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']
from rest_framework import serializers

from jobs.models import Job

class JobSerializer(serializers.ModelSerializer):
    # Don't render filepath to users
    results = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Job
        fields = "__all__"

from rest_framework import serializers

from jobs.models import Job


class JobSerializer(serializers.ModelSerializer):
    """Serializer of a Job object without rendering file path to users."""

    results = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Job
        fields = "__all__"

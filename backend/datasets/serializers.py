from rest_framework import serializers

from datasets.models import Dataset


class DatasetSerializer(serializers.ModelSerializer):
    """Serializer of a Dataset object without rendering file path to users."""

    file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Dataset
        fields = "__all__"

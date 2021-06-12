from rest_framework import serializers

from datasets.models import Dataset

class DatasetSerializer(serializers.ModelSerializer):
    # Don't render filepath to users
    file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Dataset
        fields = "__all__"

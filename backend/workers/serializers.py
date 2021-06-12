from rest_framework import serializers

from workers.models import Worker


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = "__all__"
        read_only_fields = ("ip", "registration_time")

    def create(self, validated_data):
        validated_data["ip"] = self.context.get("request").headers["X-Forwarded-For"]
        return super().create(validated_data)

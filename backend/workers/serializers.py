from rest_framework import serializers

from workers.models import Worker


class WorkerSerializer(serializers.ModelSerializer):
    """Serializer of a Worker object."""

    class Meta:
        model = Worker
        fields = "__all__"
        read_only_fields = ("ip", "registration_time")
        depth = 1

    def create(self, validated_data):
        """Hook Worker creation to add IP address of the associated
        container. This IP is used to find and kill the container
        when the job is finished.

        Args:
            validated_data (dict): Validated data used to create
                the Worker object.

        Returns:
            Worker: Worker object created from validated data.
        """
        validated_data["ip"] = self.context.get("request").headers["X-Forwarded-For"]
        return super().create(validated_data)

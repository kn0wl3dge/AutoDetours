from rest_framework import serializers

from jobs.models import Job, JobDetours, JobPESieve

class JobSerializer(serializers.ModelSerializer):
    # Don't render filepath to users
    results = serializers.FileField(write_only=True)

    # Return Job class childs attributes
    def to_representation(self, instance):
        if isinstance(instance, JobDetours):
            return JobDetoursSerializer(instance=instance).data
        elif isinstance(instance, JobPESieve):
            return JobPESieveSerializer(instance=instance).data
        else:
            return LaySerializer(instance=instance).data

    class Meta:
        model = Job
        fields = "__all__"


class JobRawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"


class JobDetoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"


class JobPESieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"
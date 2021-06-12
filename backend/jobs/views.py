from rest_framework import viewsets, mixins, renderers


class JobSubClassFieldsMixin(object):
    def get_queryset(self):
        return Job.objects.select_subclasses()

class RetrievePersonAPIView(
    JobSubClassFieldsMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = JobListSerializer

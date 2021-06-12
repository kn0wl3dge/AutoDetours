from django.urls import path, include
from rest_framework import routers

from datasets.views import DatasetViewSet
from malwares.views import MalwareViewSet
from workers.views import WorkerViewSet
# from stats.views import StatsView
from tags.views import RuleFormView
from jobs.views import JobViewSet

router = routers.DefaultRouter()
router.register(r"malwares", MalwareViewSet)
router.register(r"workers", WorkerViewSet)
router.register(r"jobs", JobViewSet)
router.register(r"datasets", DatasetViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    # path("api/stats/", StatsView.as_view()),
    path("api/rules/", RuleFormView.as_view()),
]

from django.urls import path, include
from rest_framework import routers

from malwares.views import (
    MalwareViewSet,
    DatasetGenerationView,
    DatasetDownloadView,
    DatasetCheckView,
)
from workers.views import WorkerViewSet
from stats.views import StatsView
from tags.views import RuleFormView

router = routers.DefaultRouter()
router.register(r"malwares", MalwareViewSet)
router.register(r"workers", WorkerViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/stats/", StatsView.as_view()),
    path("api/rules/", RuleFormView.as_view()),
    path("api/dataset/generate/", DatasetGenerationView.as_view()),
    path("api/dataset/download/", DatasetDownloadView.as_view()),
    path("api/dataset/download/<slug:pk>/", DatasetDownloadView.as_view()),
    path("api/dataset/check/", DatasetCheckView.as_view()),
    path("api/dataset/check/<slug:pk>/", DatasetCheckView.as_view()),
]

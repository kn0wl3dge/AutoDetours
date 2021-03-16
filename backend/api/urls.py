"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from malwaredb.views import MalwareViewSet, DatasetGenerationView, DatasetDownloadView
from workers.views import WorkerViewSet
from stats.views import StatsView

router = routers.DefaultRouter()
router.register(r'malwares', MalwareViewSet)
router.register(r'workers', WorkerViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/stats/', StatsView.as_view()),
    path('api/dataset/generate/', DatasetGenerationView.as_view()),
    path('api/dataset/download/', DatasetDownloadView.as_view()),
    path('api/dataset/download/<slug:pk>/', DatasetDownloadView.as_view())
]
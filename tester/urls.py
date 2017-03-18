from django.conf.urls import url
from django.contrib import admin

from stations.api.views import (
	# PostCreateAPIView,
	# PostDeleteAPIView,
	StationListAPIView,
	# PostDetailAPIView,
	# PostUpdateAPIView
	)

urlpatterns = [
	url(r'^$', StationListAPIView.as_view(), name='list'),
]
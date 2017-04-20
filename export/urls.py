from django.conf.urls import url
from django.contrib import admin

# from stations.api.views import (
# 	# PostCreateAPIView,
# 	# PostDeleteAPIView,
# 	StationListAPIView,
# 	# PostDetailAPIView,
# 	# PostUpdateAPIView
# 	)
from .views import export_performing
from . import views

urlpatterns = [
	url(r'^$', views.export_performing, name='export'),
]
from django.shortcuts import render

# Create your views here.
from django.db.models import Q

from rest_framework.filters import (
	SearchFilter,
	OrderingFilter,
	)

from rest_framework .generics import (
	CreateAPIView,
	DestroyAPIView,
	ListAPIView,
	UpdateAPIView,
	RetrieveAPIView,
	RetrieveUpdateAPIView
	)


# from rest_framework.permissions import (
# 	AllowAny,
# 	IsAuthenticated,
# 	IsAdminUser,
# 	IsAuthenticatedOrReadOnly,
# 	)

from production.models import Station

from .pagination import StationLimitOffsetPagination,StationPageNumberPagination

# from .permissions import IsOwnerOrReadOnly

from .serializers import (
	# PostCreateUpdateSerializer,
	# PostDetailSerializer,
	StationListSerializer
	)

# class PostCreateAPIView(CreateAPIView):
# 	queryset=Post.objects.all()
# 	serializer_class=PostCreateUpdateSerializer
# 	# permission_classes = [IsAuthenticated]

# 	def perform_create(self,serializer):
# 		serializer.save(user=self.request.user)


# class PostDetailAPIView(RetrieveAPIView):
# 	queryset=Post.objects.all()
# 	serializer_class=PostDetailSerializer
# 	lookup_field='slug'
# 	permission_classes = [AllowAny]

# 	# lookup_url_kwarg='abc'

# class PostUpdateAPIView(RetrieveUpdateAPIView):
# 	queryset=Post.objects.all()
# 	serializer_class=PostCreateUpdateSerializer
# 	lookup_field='slug'
# 	permission_classes = [IsOwnerOrReadOnly]

# 	def perform_update(self,serializer):
# 		serializer.save(user=self.request.user)

# class PostDeleteAPIView(DestroyAPIView):
# 	queryset=Post.objects.all()
# 	serializer_class=PostDetailSerializer
# 	lookup_field='slug'
	# permission_classes = [IsOwnerOrReadOnly]

class StationListAPIView(ListAPIView):
	# queryset=Post.objects.all()
	serializer_class=StationListSerializer
	filter_backends=[SearchFilter,OrderingFilter]
	# permission_classes = [AllowAny]
	search_fields =['station','family__name','name','description']
	# filter_fields = ['station']
	# pagination_class = StationPageNumberPagination

	def get_queryset(self,*args,**kwargs):
		queryset_list=Station.objects.all()
		query = self.request.GET.get("family")
		if query:
			# queryset_list = queryset_list.filter(
			# 		Q(station=query)|
			# 		Q(description__icontains=query)|
			# 		Q(name__icontains=query)
			# 		).distinct()
			queryset_list = queryset_list.filter(
					Q(family__name=query)&
					Q(critical=True)
					).exclude(family__isnull=True).distinct()
		return queryset_list
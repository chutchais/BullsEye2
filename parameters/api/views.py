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

from production.models import Parameter

from .pagination import ParameterLimitOffsetPagination,ParameterPageNumberPagination

# from .permissions import IsOwnerOrReadOnly

from .serializers import (
	# PostCreateUpdateSerializer,
	# PostDetailSerializer,
	ParameterListSerializer
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

class ParameterListAPIView(ListAPIView):
	# queryset=Post.objects.all()
	serializer_class=ParameterListSerializer
	filter_backends=[SearchFilter,OrderingFilter]
	# permission_classes = [AllowAny]
	search_fields =['name','description','station__station','station__description']
	pagination_class = ParameterPageNumberPagination

	def get_queryset(self,*args,**kwargs):
		queryset_list=Parameter.objects.filter(station__isnull=False , activated=True)
		query = self.request.GET.get("q")
		if query:
			queryset_list = queryset_list.filter(
					Q(description__icontains=query)|
					Q(name__icontains=query)|
					Q(station__station__icontains=query)|
					Q(station__description__icontains=query)|
					Q(station__family__name__icontains=query)
					).distinct()
		return queryset_list
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
	ParameterListSerializer,
	ParameterLiteListSerializer
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
	# pagination_class = ParameterPageNumberPagination
	filter_fields = ['name']

	def get_queryset(self,*args,**kwargs):
		queryset_list=None
		# default_critical="False"
		station = self.request.GET.get("station")
		family = self.request.GET.get("family")
		critical = self.request.GET.get("critical")
		if critical:
			kwargs_param={'station__station' :station,'station__family__name':family,'critical': critical}
		else:
			kwargs_param={'station__station' :station,'station__family__name':family}

		if station and family:
			queryset_list=Parameter.objects.filter(**kwargs_param).order_by('-critical','name')
		elif family:
			queryset_list=Parameter.objects.filter(station__family__name=family,
				critical=critical).order_by('-critical','name')
		# else :
		# 	queryset_list=Parameter.objects.filter(critical=critical)
		
		return queryset_list


class ParameterLiteListAPIView(ListAPIView):
	# queryset=Post.objects.all()
	serializer_class=ParameterLiteListSerializer
	filter_backends=[SearchFilter,OrderingFilter]
	# permission_classes = [AllowAny]
	# search_fields =['name','description','station__station','station__description']
	# pagination_class = ParameterPageNumberPagination
	# filter_fields = ['name']

	def get_queryset(self,*args,**kwargs):
		queryset_list=None
		default_critical=False
		station = self.request.GET.get("station")
		family = self.request.GET.get("family")
		# critical = self.request.GET.get("critical",default_critical)
		if family:
			queryset_list=Parameter.objects.filter(station__family__name=family).order_by('name')

		if family and station:
			queryset_list=Parameter.objects.filter(station__family__name=family,
				station__station =station).order_by('name')

		# if station and family:
		# 	queryset_list=Parameter.objects.filter(station__station =station,
		# 		station__family__name=family,critical=critical)
		# elif family:
		# 	queryset_list=Parameter.objects.filter(station__family__name=family,
		# 		critical=critical)
		# else :
		# 	queryset_list=Parameter.objects.filter(critical=critical)
		
		return queryset_list
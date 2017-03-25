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

from production.models import Tester

# from .pagination import FamilyLimitOffsetPagination,FamilyPageNumberPagination

# from .permissions import IsOwnerOrReadOnly

from .serializers import (
	# PostCreateUpdateSerializer,
	# PostDetailSerializer,
	TesterListSerializer
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

class TesterListAPIView(ListAPIView):
	# queryset=Post.objects.all()
	serializer_class=TesterListSerializer
	filter_backends=[SearchFilter,OrderingFilter]
	# permission_classes = [AllowAny]
	search_fields =['name']
	# pagination_class = StationPageNumberPagination

	def get_queryset(self,*args,**kwargs):
		onlytester = self.request.GET.get("onlytester")
		family = self.request.GET.get("family")
		station = self.request.GET.get("station")
		tester = self.request.GET.get("tester")
		if onlytester:
			queryset_list = Tester.objects.filter(
					Q(spc_control=True) &
					Q (station__family=family)
					).distinct('name','station__station')
		else:
			kwarg={"spc_control":"True","station__family":family}
			if tester :
				kwarg={"spc_control":"True","station__family":family,"station__station":station,"name":tester}
			queryset_list=Tester.objects.filter(**kwarg).order_by('name','station','spc_ordering')
			# queryset_list=Tester.objects.filter(
			# 	Q(spc_control=True),
			# 	Q(station__family=family)
			# 	).order_by('name','station','spc_ordering')

		# if spc_control :
		# 	queryset_list=Family.objects.filter(spc_control=True).order_by('spc_ordering')
		# else:
		# 	queryset_list=Family.objects.filter(critical=True).order_by('ordering')
		
		# query = self.request.GET.get("q")
		# if query:
		# 	queryset_list = queryset_list.filter(
		# 			Q(station__icontains=query)|
		# 			Q(description__icontains=query)|
		# 			Q(name__icontains=query)
		# 			).distinct()
		return queryset_list
from rest_framework.pagination import (
	LimitOffsetPagination,
	PageNumberPagination,
	)


class ParameterLimitOffsetPagination(LimitOffsetPagination):
	default_limit =20
	max_limit=50


class ParameterPageNumberPagination(PageNumberPagination):
	page_size=20

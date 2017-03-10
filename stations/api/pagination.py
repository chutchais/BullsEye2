from rest_framework.pagination import (
	LimitOffsetPagination,
	PageNumberPagination,
	)


class StationLimitOffsetPagination(LimitOffsetPagination):
	default_limit =20
	max_limit=50


class StationPageNumberPagination(PageNumberPagination):
	page_size=20
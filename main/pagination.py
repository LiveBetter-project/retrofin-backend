from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class ItemsPagePagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100

    def get_paginated_response(self, data):
        limit = self.get_limit(self.request) or self.default_limit
        offset = self.get_offset(self.request) or 0
        return Response({
            "items": data,
            "page": {
                "limit": limit,
                "offset": offset,
                "total": self.count,
            }
        })
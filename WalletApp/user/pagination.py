from rest_framework import pagination
from rest_framework.response import Response
from .response_handler import ResponseHandler


class TransactionListPagination(pagination.PageNumberPagination):
    response_handler = ResponseHandler()
    page_size = 10  # Default page size
    page_size_query_param = "page_size"
    max_page_size = 5000

    def get_paginated_response(self, data):
        context = {
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        }
        response_dict, status_code = self.response_handler.success(
            data=context,
            msg="Transaction data fetched successfully!",
        )
        return Response(response_dict)
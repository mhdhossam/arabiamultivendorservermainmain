from rest_framework import pagination


class OrderItemPagination(pagination.PageNumberPagination):
    page_size = 25
    max_page_size = 50
    page_query_param = "p"
    page_size_query_param = "l"


class ReturnRequestPagination(pagination.PageNumberPagination):
    page_size = 25
    max_page_size = 50
    page_query_param = "p"
    page_size_query_param = "l"

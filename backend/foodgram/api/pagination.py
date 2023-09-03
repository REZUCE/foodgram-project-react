from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    # Используем 'limit' для указания количества объектов на странице
    page_size_query_param = 'limit'
    # Количество объектов на одной странице
    page_size = 6
    # Используем 'page' для указания номера страницы
    page_query_param = 'page'


from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    # Количество объектов на одной странице
    page_size = 10
    # # Используем 'limit' для указания количества объектов на странице
    # page_size_query_param = 'limit'
    # max_page_size = 100
    # Используем 'page' для указания номера страницы
    page_query_param = 'page'

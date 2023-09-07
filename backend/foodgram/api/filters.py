from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    author = filters.CharFilter()
    tags = filters.ModelMultipleChoiceFilter(
        # Обращаемся к связанному полю.
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        # Устанавливаем метку "Теги" для фильтра.
        label='Tags',

        to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author')

    def get_is_favorited(self, queryset, name, value):
        """Фильтрация queryset по полю is_favorited."""

        if value and self.request.user.is_authenticated:
            # Обращение к таблице Favorite через related_name.
            # В избранном только те рецепты, которые есть в избранном
            # у пользователя отправившего запрос.
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация queryset по полю is_in_shopping_cart."""

        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset



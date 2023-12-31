import weasyprint
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny
)
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST,
                                   HTTP_204_NO_CONTENT)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Tag, Recipe, Ingredient,
                            Favorite, ShoppingCart,
                            RecipeIngredient)
from users.models import CustomUser
from users.models import Subscription
from .filters import RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (TagSerializer, RecipesSerializer,
                          RecipeCreateSerializer, IngredientSerializer,
                          SubscriptionSerializer, ShowSubscriptionSerializer,
                          CustomUserSerializer, ShortRecipeSerializer)


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        data = {
            'user': request.user.pk,
            'author': id
        }
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data=data,
                context={'request': request}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    serializer.data, status=HTTP_201_CREATED)
            return Response(status=HTTP_400_BAD_REQUEST)
        author = get_object_or_404(CustomUser, id=id)
        if Subscription.objects.filter(
                user=request.user,
                author=author).exists():
            subscription = get_object_or_404(
                Subscription, user=request.user, author=author
            )
            subscription.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)

    @action(
        methods=("get",),
        detail=False,
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPagination
    )
    def subscriptions(self, request):
        """
        Получить пользователей на которых подписан текущий пользователь.
        """
        subscription = CustomUser.objects.filter(author__user=request.user)
        page = self.paginate_queryset(subscription)
        serializer = ShowSubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )

        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        """
        Для оптимизации запросов к бд.
        """

        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'recipe_tags__tag'
        ).all()
        return recipes

    def get_serializer_class(self):
        """
        Под каждый тип запросов свой serializer.
        """

        if self.request.method == 'GET':
            return RecipesSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_to_model(self, model, user, pk):
        if not model.objects.filter(
                user=user, recipe__id=pk
        ).exists():
            recipe = get_object_or_404(Recipe, id=pk)
            model.objects.create(recipe=recipe, user=user)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST)

    def delete_from_model(self, model, user, pk):
        if model.objects.filter(
                user=user,
                recipe__id=pk).exists():
            model.objects.filter(
                user=user,
                recipe__id=pk
            ).delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to_model(Favorite, request.user, pk)
        else:
            return self.delete_from_model(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to_model(ShoppingCart, request.user, pk)
        return self.delete_from_model(ShoppingCart, request.user, pk)


@api_view(['GET'])
def download_shopping(request):
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values('ingredient__name', 'ingredient__measurement_unit', ).annotate(
        amount=Sum('amount')
    )
    # Передаем значение в pdf.
    html = render_to_string('ingredients_buy.html',
                            {'ingredients': ingredients})
    # Указываем тип содержимого.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=wish_list.pdf'
    weasyprint.HTML(string=html).write_pdf(response)
    return response

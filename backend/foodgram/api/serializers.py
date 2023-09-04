from rest_framework import serializers
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer, UserCreateSerializer
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from users.models import CustomUser, Subscription
from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient, RecipeTag, Favorite, ShoppingCart
import webcolors

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор создания пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """
        Дополнительное поле - проверка подписки, которое
        никак не взаимодействует с базой данных.
        """

        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        # obj - это сериализуемый пользователь
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор модели пользователя."""

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class ShowSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения подписок на пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',  # рецепты должны относится к опредленному пользователю
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        # Если пользователь анонимный, то вернуть False
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        return ShowFavoriteSerializer(recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериазитор создания подписки."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def to_representation(self, instance):
        return ShowSubscriptionSerializer(instance.author, context={
            'request': self.context.get('request')
        }).data


class Hex2NameColor(serializers.Field):
    """
    Собственный тип суриализатора.
    В режиме записи конвертирует код цвета в его название,
    В режиме чтения вернёт название цвета из БД.
    """

    # При чтении данных ничего не меняем - просто возвращаем как есть
    def to_representation(self, value):
        return value

    # При записи код цвета конвертируется в его название
    def to_internal_value(self, data):
        # Доверяй, но проверяй
        try:
            # Если имя цвета существует, то конвертируем код в название.
            # data - hex формат, на который мы проверяем название цвета на сайте.
            data = webcolors.hex_to_name(data)
        except ValueError:
            # Иначе возвращаем ошибку
            raise serializers.ValidationError('Для этого цвета нет имени')
        # Возвращаем данные в новом формате
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели тег."""

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиент."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели, которая связывает рецепт и ингредиенты."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецепт."""

    tags = TagSerializer(many=True)
    # Получай ингредиенты из связанной модели
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name',
                  'text', 'cooking_time',
                  'image'
                  )

    def get_is_favorited(self, obj):
        """
        Дополнительное поле, которое
        никак не взаимодействует с базой данных.
        """
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        # obj - это сериализуемый пользователь
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Дополнительное поле, которое
        никак не взаимодействует с базой данных.
        """
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        # obj - это сериализуемый пользователь
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецепт - для создания/обновления."""

    ingredients = RecipeIngredientCreateSerializer(many=True)

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        """
        Создание рецепта.
        Делаем, чтобы сделать связь m2m.
        """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')  # Уберите 'tags' из validated_data
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=ingredient["ingredient"],
                amount=ingredient["amount"],
                recipe=recipe
            )
        return recipe

    def update(self, instance, validated_data):
        """
        Изменение рецепта.
        Доступно только автору.
        Делаем, чтобы сделать связь m2m.
        """

        RecipeTag.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for tag in tags:
            RecipeTag.objects.create(recipe=instance, tag=tag)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=ingredient["ingredient"],
                amount=ingredient["amount"],
                recipe=instance
            )
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image'):
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        return instance

    def to_representation(self, instance):
        # instance: Это объект модели, который вы хотите сериализовать.
        #  Атрибут context у сериализатора содержит контекст,
        #  в котором происходит сериализация. В вашем коде вы
        #  извлекаете объект запроса request из контекста, чтобы
        #  передать его внутрь сериализатора RecipesSerializer.
        context = {"request": self.context.get("request")}
        # Когда вы хотите получить представление объекта в виде словаря,
        # который может быть преобразован в JSON или другой формат,
        # вы используете .data.
        return RecipesSerializer(instance, context=context).data


class ShowFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения избранного."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели избранного."""

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class ShowShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения Списка покупок."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор модели Списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return ShowShoppingCartSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data

import webcolors
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Tag, Recipe, RecipeIngredient,
                            Ingredient, RecipeTag, Favorite,
                            ShoppingCart)
from users.models import CustomUser
from users.models import Subscription


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

        return (
                request.user.is_authenticated
                and request.user.subscription.exists()
        )


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
    recipes_count = serializers.ReadOnlyField(source='user_recipes.count')

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
                request.user.is_authenticated
                and request.user.subscription.exists()
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        return ShowFavoriteSerializer(
            recipes, many=True,
            context={'request': request}
        ).data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериазитор создания подписки."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def to_representation(self, instance):
        return ShowSubscriptionSerializer(
            instance.author, context=self.context
        ).data

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        return data


class Hex2NameColor(serializers.Field):
    """
    Собственный тип суриализатора.
    В режиме записи конвертирует код цвета в его название,
    В режиме чтения вернёт название цвета из БД.
    """

    def to_representation(self, value):
        return value

    def validate_hex(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data

    def to_internal_value(self, data):
        self.validate_hex(data)


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

        return (
                request.user.is_authenticated
                and request.user.favorites.exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """
        Дополнительное поле, которое
        никак не взаимодействует с базой данных.
        """

        request = self.context.get('request')
        return (
                request.user.is_authenticated
                and request.user.shopping_cart.exists()
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'measurement_unit')

    validators = [
        UniqueTogetherValidator(
            queryset=Ingredient.objects.all(),
            fields=('name', 'measurement_unit')
        )
    ]


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

    def validate_tags(self, tags):
        list_tags = []
        if not tags:
            raise serializers.ValidationError(
                'Хотя бы один тег должен быть.'
            )
        for tag in list_tags:
            if tag['id'] in list_tags:
                raise serializers.ValidationError(
                    'Тег должен быть уникальным.'
                )
            list_tags.append(tag['id'])

    def validate_ingredients(self, ingredients):
        list_ingredients = []
        if not ingredients:
            raise serializers.ValidationError(
                'Хотя бы один ингредиент должен быть.'
            )
        for ingredient in list_ingredients:
            if ingredient['id'] in list_ingredients:
                raise serializers.ValidationError(
                    'Ингредиент должен быть уникальным.'
                )
            list_ingredients.append(ingredient['id'])

    def validate_cooking_time(self, value):
        if not 120 >= value >= 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть положительным числом '
                'и меньше 2 часов (120 минут).'
            )

    def create(self, validated_data):
        """
        Создание рецепта.
        Делаем, чтобы сделать связь m2m.
        """

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
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
        context = {"request": self.context.get("request")}
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


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения списка покупок и избранного."""

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

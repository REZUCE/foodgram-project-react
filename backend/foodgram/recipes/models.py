from django.db import models
from django.db.models import UniqueConstraint

from core.parametrs import Parameters
from users.models import CustomUser
from .validators import (
    validate_slug,
    validate_cooking_time,
    validate_recipe_ingredient)


class Ingredient(models.Model):
    """Модель Ингредиентов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=Parameters.MAX_LEN_INT_RECIPES.value
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерение',
        max_length=Parameters.MAX_LEN_INT_RECIPES.value
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='name_measurement_unit_unique'
            )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f"{self.name} - вес в  {self.measurement_unit}"


class IngredientImport(models.Model):
    """Модель для сохранения истории импортов."""

    csv_file = models.FileField(upload_to='uploads/')
    date_added = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=Parameters.MAX_LEN_INT_RECIPES.value,
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=Parameters.MAX_LEN_INT_COLOR.value
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        unique=True,
        validators=[validate_slug]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return f"{self.name}"


class Recipe(models.Model):
    """Модель рецептов."""

    tags = models.ManyToManyField(
        to=Tag,
        verbose_name='Теги',
        through='RecipeTag',
    )
    author = models.ForeignKey(
        to=CustomUser,
        related_name='user_recipes',
        verbose_name='Пользователь (В рецепте - автор рецепта)',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        verbose_name='Ингридиенты',
        through='RecipeIngredient',

    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/'
    )

    text = models.TextField(
        verbose_name='Описание'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=Parameters.MAX_LEN_INT_RECIPES.value
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[validate_cooking_time]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации.',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        # В порядке убывания
        ordering = ('pub_date',)

    def __str__(self) -> str:
        return f"{self.name}"


class RecipeIngredient(models.Model):
    """Связь M2M Recipe модели и Ingredient."""

    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[validate_recipe_ingredient]
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='recipe_ingredient_unique'
            )
        ]
        verbose_name = 'M2M RecipeIngredient'
        verbose_name_plural = 'M2M RecipesIngredients'

    def __str__(self) -> str:
        return f"{self.recipe} {self.ingredient}"


class RecipeTag(models.Model):
    """Связь M2M Recipe модели и Tag"""

    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Рецепт',
        related_name='recipe_tags',
        on_delete=models.CASCADE

    )
    tag = models.ForeignKey(
        to=Tag,
        verbose_name='Тег',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'tag'),
                name='recipe_tag_unique'
            )
        ]
        verbose_name = 'M2M RecipeTag'
        verbose_name_plural = 'M2M RecipeTag'

    def __str__(self) -> str:
        return f"{self.recipe} {self.tag}"


class ShoppingCart(models.Model):
    """Модель корзины."""

    user = models.ForeignKey(
        to=CustomUser,
        verbose_name='Пользователь',
        related_name='shopping_cart',
        on_delete=models.CASCADE,

    )
    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Рецепт',
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='shopping_cart_recipe_user'
            )
        ]
        verbose_name = 'M2M RecipeUserShoppingCart'
        verbose_name_plural = 'M2M RecipeUserShoppingCart'

    def __str__(self) -> str:
        return f"{self.recipe} - {self.user}"


class Favorite(models.Model):
    """Модель избранного."""

    user = models.ForeignKey(
        to=CustomUser,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=models.CASCADE,

    )
    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Рецепт',
        related_name='favorites',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='favorite_recipe_user'
            )
        ]
        verbose_name = 'M2M Избранный'
        verbose_name_plural = 'M2M Избранные'

    def __str__(self) -> str:
        return f"{self.recipe} - {self.user}"

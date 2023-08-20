from django.db import models

from django.contrib.auth import get_user_model
from .validators import (
    validate_slug,
    validate_cooking_time,
    validate_recipe_ingredient)

User = get_user_model()


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=7
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
        verbose_name='Список тегов'
    )
    author = models.ForeignKey(
        to=User,
        verbose_name='Пользователь (В рецепте - автор рецепта)',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        to='Ingredient',
        # Но при этом нам нужно, чтобы ингредиенты
        # относились именно к этому рецепту
        through='RecipeIngredient',
        verbose_name='Ингридиенты'
    )
    # is_favorited
    # is_in_shopping_cart
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    # image
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[validate_cooking_time]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return f"{self.name}"


class Ingredient(models.Model):
    """Модель Ингредиентов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Измерение',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f"{self.name} - вес в  {self.measurement_unit}"


class RecipeIngredient(models.Model):
    """Связь M2M Recipe модели и Ingredient."""

    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Рецепт',
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
        verbose_name = 'M2M RecipeIngredient'
        verbose_name_plural = 'M2M RecipesIngredients'

    def __str__(self) -> str:
        return f"{self.recipe} {self.ingredient}"

from re import match
from core.parametrs import Parameters
from django.core.exceptions import ValidationError


def validate_slug(value):
    pattern = r'^[-a-zA-Z0-9_]+$'
    if not match(pattern, value):
        raise ValidationError(
            'Slug может содержать только латинские буквы, '
            'цифры, дефисы и подчеркивания.'
        )
    return value


def validate_cooking_time(value):
    if not 120 >= value >= 1:
        raise ValidationError(
            'Время приготовления должно быть положительным числом '
            'и меньше 2 часов (120 минут).'
        )


def validate_recipe_ingredient(value):
    if not 100 >= value >= 1:
        raise ValidationError(
            'Значение не должно быть меньше 1 или больше 100.'
        )

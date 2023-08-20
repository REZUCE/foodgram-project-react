from django.core.exceptions import ValidationError
from re import match


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

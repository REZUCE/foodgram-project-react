from re import match

from django.core.exceptions import ValidationError


def validate_username(value):
    pattern = r'^[\w.@+-]+$'
    if not match(pattern, value):
        raise ValidationError(
            "Имя пользователя может содержать только буквы, "
            "цифры, '_', '.', '@', '+' и '-'."
        )
    return value

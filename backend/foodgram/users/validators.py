from django.core.exceptions import ValidationError
from re import match


def validate_username(value):
    pattern = r'^[\w.@+-]+$'
    if not match(pattern, value):
        raise ValidationError(
            "Имя пользователя может содержать только буквы, "
            "цифры, '_', '.', '@', '+' и '-'."
        )
    return value

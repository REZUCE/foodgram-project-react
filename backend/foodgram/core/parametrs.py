from enum import IntEnum


class Parameters(IntEnum):
    # В приложении users.models:
    MAX_LEN_EMAIL = 254
    MAX_LEN_CHAR_FIELD_USERS = 50
    # В приложении recipes.models и recipes.validators:
    MAX_LEN_INT_RECIPES = 200
    MAX_LEN_INT_COLOR = 7
    VALIDATE_COOKING_TIME_MIN = 1
    VALIDATE_COOKING_TIME_MAX = 120

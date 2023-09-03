from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_username
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
    )

    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=150,
        unique=True,
        validators=[validate_username]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )

    password = models.CharField(
        verbose_name='Пароль',
        max_length=150
    )

    # Замена логина.
    USERNAME_FIELD = 'email'
    # Что будет запрашиваться при createsuperuser
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ("username",)

    def __str__(self) -> str:
        return f"{self.username}: {self.email}"


class Subscription(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        to=CustomUser,
        verbose_name='Подписчик',
        related_name='followers',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        to=CustomUser,
        verbose_name='Автор',
        related_name='author',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'M2M Подписка'
        verbose_name_plural = 'M2M Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_name_owner',
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username} подписан на {self.author.username}'

    def clean(self):
        """
        Это дополнительный метод,
        который срабатывает перед сохранением.
        """
        if self.user == self.author:
            raise ValidationError("На себя нельзя подписаться!")

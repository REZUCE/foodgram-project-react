from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Subscription

User = get_user_model()
admin.site.register(Subscription)


class UsernameFilterCustomUser(SimpleListFilter):
    title = _('Username Filter')

    # Берем из модели user поле email.
    parameter_name = "username"

    def lookups(self, request, model_admin):
        """В алфавитном порядке."""
        # values_list - получает список, а внутри него кортеж.
        # flat=True, помогает все достать из кортежа и закинуть
        # в список.
        unique_first_latters = User.objects.values_list(
            'username', flat=True
        ).distinct()
        print(unique_first_latters)
        return [(letter[0], letter[0]) for letter in unique_first_latters]

    def queryset(self, request, queryset):
        """Выдача значений после фильтрации."""

        value = self.value()
        if not value:
            return queryset
        return queryset.filter(username__startswith=value)


class FilterCustomUser(admin.ModelAdmin):
    list_filter = (UsernameFilterCustomUser, 'email',)


admin.site.register(CustomUser, FilterCustomUser)

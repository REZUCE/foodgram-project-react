import csv

from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path
from django.urls import reverse
from users.admin import UsernameFilterCustomUser

from .forms import IngredientImportForm
from .models import (
    Tag, Recipe, Ingredient,
    RecipeIngredient, RecipeTag,
    Favorite, ShoppingCart, IngredientImport
)

admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)


class RecipeIngredientInline(admin.TabularInline):
    """Позволяет редактировать связанные объекты."""

    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    """Позволяет редактировать связанные объекты."""

    model = RecipeTag
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, RecipeTagInline,)
    list_filter = ('tags', 'name', 'author',)


# Отображает панель для модели BookImport.
@admin.register(IngredientImport)
class BookImportAdmin(admin.ModelAdmin):
    list_display = ('csv_file', 'date_added',)


# Отображает панель для модели Book и метод для импорта.
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)

    # Даем django(urlpatterns) знать
    # о существовании страницы с формой
    # иначе будет ошибка.
    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('csv-upload/', self.upload_csv))
        return urls

    # Если пользователь открыл url 'csv-upload/'
    # то он выполнит этот метод
    # который работает с формой.
    def upload_csv(self, request):
        if request.method == 'POST':
            form = IngredientImportForm(request.POST, request.FILES)
            if form.is_valid():
                # Сохраняем загруженный файл и делаем запись в базу.
                form_object = form.save()
                # Обработка csv файла.
                with form_object.csv_file.open('r') as csv_file:
                    rows = csv.reader(csv_file, delimiter=',')
                    if next(rows) != ['name', 'measurement_unit']:
                        # Обновляем страницу пользователя
                        # с информацией о какой-то ошибке.
                        messages.warning(
                            request, 'Неверные заголовки у файла'
                        )
                        # Перенаправление на тот url, с которого
                        # отправили запрос.
                        return HttpResponseRedirect(
                            request.path_info
                        )
                    for row in rows:
                        # Добавляем данные в базу.
                        Ingredient.objects.update_or_create(
                            name=row[0],
                            measurement_unit=row[1],
                        )
                # Конец обработки файлы
                # перенаправляем пользователя на главную страницу
                # с сообщением об успехе.
                url = reverse('admin:index')
                messages.success(request, 'Файл успешно импортирован')
                return HttpResponseRedirect(url)
        form = IngredientImportForm()
        return render(request, 'admin/csv_import_page.html', {'form': form})

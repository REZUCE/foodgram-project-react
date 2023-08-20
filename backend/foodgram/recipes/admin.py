from django.contrib import admin

from .models import Tag, Recipe, Ingredient, RecipeIngredient

admin.site.register(Tag)
admin.site.register(Ingredient)


class RecipeIngredientInline(admin.TabularInline):
    """Позволяет редактировать связанные объекты."""

    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)

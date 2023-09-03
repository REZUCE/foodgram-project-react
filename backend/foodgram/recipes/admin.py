from django.contrib import admin

from .models import Tag, Recipe, Ingredient, RecipeIngredient, RecipeTag, Favorite, ShoppingCart

admin.site.register(Tag)
admin.site.register(Ingredient)
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

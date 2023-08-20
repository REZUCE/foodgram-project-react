from django.contrib import admin

from .models import Tag, Recipe

admin.site.register(Tag)
admin.site.register(Recipe)

from django.contrib import admin
from recipes.models import (Favorite, Ingredient, Link, Recipe,
                            RecipeIngredients, ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredients


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'is_favorited')
    search_fields = ('name', 'author__username')
    list_filter = ('name', 'author', 'tags')
    inlines = [
        RecipeIngredientsInline,
    ]

    @admin.display(description='количество добавлений в избранное')
    def is_favorited(self, recipe):
        return recipe.favorite.count()


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'original_url', 'short_link')

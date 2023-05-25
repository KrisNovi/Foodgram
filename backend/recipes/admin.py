from django.contrib import admin

from .models import (Favorite, Ingredients, IngredientsInRecipe, Recipe,
                     ShoppingCart, Tag)


@admin.register(IngredientsInRecipe)
class IngredientsInRecipeAdmin(admin.ModelAdmin):
    fields = ('recipe', 'ingredients', 'amount', )
    search_fields = ('name', )


class IngredientsInRecipeInline(admin.TabularInline):
    model = IngredientsInRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'text',
        'image',
        'cooking_time'
    )
    search_fields = ('name',)
    list_filter = ('author', )
    filter_horizontal = ('tags',)
    autocomplete_fields = ('ingredients',)
    inlines = (IngredientsInRecipeInline, )
    empty_value_display = '-пусто-'


@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipes')
    search_fields = ('recipes',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipes')
    search_fields = ('user', 'recipes',)

from django.contrib import admin
from .models import Recipe, Tag, Ingredient

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        # 'ingredients',
        # 'tags',
        'text',
        'image',
        'cooking_time'
    )
    # list_editable = ('group',)
    # search_fields = ('text',)
    # list_filter = ('pub_date',)
    empty_value_display = '-пусто-'

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'qty', 'measurement_unit')

admin.site.register(Tag)
# admin.site.register(Ingredient)

from django.contrib import admin
from .models import Recipe, Tag, Ingredient, RecipeIngredient

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    fields = ('ingredient', 'recipe', 'amount')
    search_fields = ('ingedient', 'recipe')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient

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
    search_fields = ('name',)
    list_filter = ('author', )
    filter_horizontal = ('tags',)
    autocomplete_fields = ('ingredients',)
    inlines = (RecipeIngredientInline, )
    

    empty_value_display = '-пусто-'

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     return qs.prefetch_related('ingredient')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)




# admin.site.register(Recipe)

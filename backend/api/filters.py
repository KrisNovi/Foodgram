import django_filters
from django_filters import filters
from recipes.models import Ingredients, Recipe


class IngredientsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = Ingredients
        fields = ['name', ]


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(
        field_name='tags__slug',
        lookup_expr='iexact',
    )
    is_favorited = filters.BooleanFilter()

    class Meta:
        model = Recipe
        fields = ['tags', 'is_favorited', ]

import django_filters
from recipes.models import Ingredients


class IngredientsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = Ingredients
        fields = ['name', ]


# class RecipeFilter(django_filters.FilterSet):
#     tags = django_filters.CharFilter(
#         field_name='tags__name',
#         lookup_expr='iexact',
#     )
#     author = django_filters.CharFilter(
#         field_name='author__username',
#         lookup_expr='icontains',
#     )
#     ingredients = django_filters.CharFilter(
#         field_name='ingredients__name',
#         lookup_expr='icontains',
#     )
#     name = django_filters.CharFilter(
#         field_name='name',
#         lookup_expr='itcontains',
#     )

#     class Meta:
#         model = Recipe
#         fields = ['tags', 'author', 'ingredients', 'name']

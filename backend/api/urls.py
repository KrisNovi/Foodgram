from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipeViewSet, TagViewSet, UserViewSet,
                    download_shopping_cart)

users_router = DefaultRouter()
users_router.register('', UserViewSet, basename='users')

recipes_router = DefaultRouter()
recipes_router.register(
    'tags', TagViewSet, basename='tags')
recipes_router.register(
    'recipes', RecipeViewSet, basename='recipes')
recipes_router.register(
    'ingredients', IngredientsViewSet, basename='ingredients')


urlpatterns = [
    path('users/', include(users_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart'
    ),
    path('', include(recipes_router.urls)),
]

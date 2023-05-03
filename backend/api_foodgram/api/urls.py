from django.urls import include, path
from rest_framework import routers

from api.views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    UserViewSet,
    # signup,
    # get_token,
)

app_name = 'api'

router = routers.DefaultRouter()

# router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    # path('v1/auth/token/', get_token, name='get_token'),
    # path('v1/auth/signup/', signup, name='signup'),
    path('auth/', include('djoser.urls')),
    # JWT-эндпоинты, для управления JWT-токенами:
    path('auth/', include('djoser.urls.authtoken')),
]
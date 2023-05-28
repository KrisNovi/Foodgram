from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef, Sum
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filter
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (Favorite, Ingredients, IngredientsInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from users.models import Subscription

from .filters import IngredientsFilter, RecipeFilter
from .serializers import (FavoriteSerializer, IngredientsSerializer,
                          RecipeSerializer, RecipeSerializerPost,
                          ShoppingCartSerializer, SubscribeSerializer,
                          SubscribeSerializerPost, TagSerializer,
                          UserCreateSerializer, UserSerializer)

User = get_user_model()


@api_view(('GET', ))
@permission_classes((permissions.IsAuthenticated,))
def download_shopping_cart(request):
    if request.method == 'GET':
        user = request.user
        favorites = ShoppingCart.objects.filter(
            user=user).values_list('recipes__id', flat=True)
        ingredients_list = IngredientsInRecipe.objects.filter(
            recipe__in=Recipe.objects.filter(id__in=favorites)).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_cart = ''
        for ingredient in ingredients_list:
            shopping_cart += (
                f'{ingredient["ingredients__name"]} - '
                f'{ingredient["amount"]} '
                f'{ingredient["ingredients__measurement_unit"]}\r\n'
            )
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    return HttpResponseNotAllowed(['GET'])


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_user(self):
        return self.request.user

    def get_queryset(self):
        if self.action in ('subscriptions', 'subscribe'):
            return self.queryset.filter(
                subscribing__user=self.get_user()).annotate(
                recipes_count=Count('recipe'),
            )
        return self.queryset

    def get_permissions(self):
        if self.action in ('create', 'list', 'reset_password', ):
            self.permission_classes = (permissions.AllowAny,)
        elif self.action == 'subscribe':
            self.permission_classes = (
                permissions.IsAuthenticatedOrReadOnly,
            )
        return super().get_permissions()

    serializer_class_by_action = {
        'create': UserCreateSerializer,
        'set_password': SetPasswordSerializer,
        'subscriptions': SubscribeSerializer,
        'subscribe': SubscribeSerializerPost,
    }

    def get_serializer_class(self):
        if hasattr(self, 'serializer_class_by_action'):
            return self.serializer_class_by_action.get(
                self.action,
                self.serializer_class
            )
        return super(UserViewSet, self).get_serializer_class()

    def perform_create(self, serializer):
        DjoserUserViewSet.perform_create(self, serializer)

    @action(
        detail=False,
        methods=['get', ]
    )
    def me(self, request, *args, **kwargs):
        user = self.get_user()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post', ],
    )
    def set_password(self, request, *args, **kwargs):
        return DjoserUserViewSet.set_password(self, request, *args, **kwargs)

    @action(
        detail=False,
        methods=['get', ],
    )
    def subscriptions(self, request, *args, **kwargs):
        context = {'request': request}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete', ]
    )
    def subscribe(self, request, pk=None):
        get_object_or_404(User, pk=pk)
        context = {'request': request}
        data = {
            'user': self.request.user.pk,
            'author': pk,
        }
        serializer = self.get_serializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        if request.method == 'DELETE':
            instance = Subscription.objects.get(**serializer.initial_data)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer.save()
        queryset = self.get_queryset().get(id=pk)
        instance_serializer = SubscribeSerializer(queryset, context=context)
        return Response(instance_serializer.data, status.HTTP_201_CREATED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None
    search_fields = ('^name',)
    filter_backends = (filter.DjangoFilterBackend,)
    filterset_class = IngredientsFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    filter_backends = (filter.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return self.queryset
        return self.queryset.annotate(
            is_favorited=Exists(
                user.fav.filter(recipes=OuterRef('pk'))),
            is_in_shopping_cart=Exists(
                user.cart.filter(recipes=OuterRef('pk'))),
        )

    serializer_class_by_action = {
        'create': RecipeSerializerPost,
        'update': RecipeSerializerPost,
        'partial_update': RecipeSerializerPost,
        'favorite': FavoriteSerializer,
        'shopping_cart': ShoppingCartSerializer,
    }

    def get_serializer_class(self):
        if hasattr(self, 'serializer_class_by_action'):
            return self.serializer_class_by_action.get(
                self.action,
                self.serializer_class
            )
        return super(RecipeViewSet, self).get_serializer_class()

    def return_status(self, instanse, status):
        instance_serializer = RecipeSerializer(
            instanse, context={'request': self.request})
        return Response(instance_serializer.data, status)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_recipe = serializer.save(author=self.request.user)

        return self.return_status(new_recipe, status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)

        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return self.return_status(instance, status.HTTP_200_OK)

    def favorite_shopping_cart(self, request, model, pk):
        serializer = self.get_serializer(
            data={'recipes': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        if request.method == 'DELETE':
            model.objects.filter(user=user, recipes=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer.save(user=self.request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['post', 'delete', ]
    )
    def favorite(self, request, pk=None):
        return self.favorite_shopping_cart(request, Favorite, pk)

    @action(
        detail=True,
        methods=['post', 'delete', ]
    )
    def shopping_cart(self, request, pk=None):
        return self.favorite_shopping_cart(request, ShoppingCart, pk)


# @api_view(('GET', ))
# @permission_classes((permissions.IsAuthenticated,))
# def favorites_list(request):
#     favorites = Favorite.objects.filter(user=request.user)
#     favorite_recipes = [f.recipes for f in favorites]
#     serializer = ShortRecipeSerializer(favorite_recipes, many=True)
#     return Response(serializer.data)

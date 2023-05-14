from rest_framework import mixins, viewsets
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient, Favorite, ShoppingCart
from django.shortcuts import get_object_or_404
from django.db.models import Count, Exists
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.status import HTTP_401_UNAUTHORIZED
from .serializers import (
    UserSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeSerializerPost,
    RecipeSerializerGet,
    UserSerializer,
    UserCreateSerializer,
    FavoriteSerializer,
    SubscribeSerializer,
    SubscriptionSerializer
)
from users.models import Subscription
from djoser.views import UserViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from api.permissions import IsRoleAdmin, IsAuthorOrReadOnly, ReadOnly
from django_filters.rest_framework import DjangoFilterBackend


User = get_user_model()

class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'subscriptions':
            return SubscriptionSerializer
        elif self.action == 'subscribe':
            return SubscribeSerializer
        return self.serializer_class

    def get_user(self):
        return self.request.user

    def get_queryset(self):
        if self.action in ('subscriptions', 'subscribe'):
            return self.queryset.filter(
                author__user=self.get_user()).annotate(
                recipes_count=Count('recipe'),
            )
        return self.queryset

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        subscribe = Subscription.objects.filter(user=user, author=author)
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'POST':
            if subscribe.exists():
                data = {
                    'errors': ('Вы уже подписаны на этого автора, '
                               'или пытаетесь подписаться на себя.')}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(user=user, author=author)
            serializer = SubscribeSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not subscribe.exists():
                data = {'errors': 'Вы не подписаны на данного автора.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # data = {
        #     'user': user.id,
        #     'author': author.id,
        # }
        # if user.is_anonymous:
        #     return Response(status=status.HTTP_401_UNAUTHORIZED)
        # if request.method == 'POST':
        #     serializer = SubscribeSerializer(
        #         data=data, context={'request': request}
        #     )
        #     serializer.is_valid(raise_exception=True)
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # get_object_or_404(
        #     Subscription, user=request.user, author=author
        # ).delete()
        # return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(follower__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    # @action(
    #     methods=['GET'],
    #     detail=False,
    #     permission_classes=[IsAuthenticated],
    # )
    # def me(self, request):
    #     if request.user.is_anonymous:
    #         return Response(status=HTTP_401_UNAUTHORIZED)
    #     serializer = UserSerializer(request.user)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['GET'],
        detail=False,)
    def me(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [ReadOnly, ]
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    search_fields = ['^name', ]
    filter_backends = (DjangoFilterBackend,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class_by_action = {
        'retrieve': RecipeSerializerGet,
        'list': RecipeSerializerGet,
        'create': RecipeSerializerPost,
        'partial_update': RecipeSerializerPost
    }
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = TitleFilter
    
    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if hasattr(self, 'serializer_class_by_action'):
            return self.serializer_class_by_action.get(
                self.action,
                self.serializer_class
            )
        return super(RecipeViewSet, self).get_serializer_class()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action == 'partial_update':
            permission_classes = [IsAuthorOrReadOnly]
        else:
            permission_classes = [IsAuthorOrReadOnly]
        return [permission() for permission in permission_classes]
    
    @staticmethod
    def create_object(serializer_class, user, recipe):
        data = {
                'user': user.id,
                'recipe': recipe.id,
            }
        serializer = serializer_class(
            data=data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(
        detail=True,
        methods=['POST', 'GET'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_favorite = Favorite.objects.filter(
            user=user, recipe=recipe
        )
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'POST':
            if not in_favorite:
                favorite = Favorite.objects.create(user=user, recipe=recipe)
                serializer = FavoriteSerializer(favorite.recipe)
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            if not in_favorite:
                data = {'errors': 'Такого рецепта нет в избранных.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            in_favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        get_object_or_404(
            Favorite,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




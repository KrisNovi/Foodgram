from rest_framework import mixins, viewsets
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient
from users.models import User
from .serializers import (
    UserSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeSerializerPost,
    RecipeSerializerGet,
    UserSerializer,
    UserCreateSerializer
)
from djoser.views import UserViewSet


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class_by_action = {
        'retrieve': UserSerializer,
        'list': UserSerializer,
        'create': UserCreateSerializer,
        # 'partial_update': TitleSerializerPost,
    }
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = TitleFilter

    def get_serializer_class(self):
        if hasattr(self, 'serializer_class_by_action'):
            return self.serializer_class_by_action.get(
                self.action,
                self.serializer_class
            )
        return super(CustomUserViewSet, self).get_serializer_class()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class_by_action = {
        'retrieve': RecipeSerializerGet,
        'list': RecipeSerializerGet,
        'create': RecipeSerializerPost,
        # 'partial_update': TitleSerializerPost,
    }
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = TitleFilter

    def get_serializer_class(self):
        if hasattr(self, 'serializer_class_by_action'):
            return self.serializer_class_by_action.get(
                self.action,
                self.serializer_class
            )
        return super(RecipeViewSet, self).get_serializer_class()

    # def get_permissions(self):
    #     if self.action in ['list', 'retrieve']:
    #         permission_classes = [AllowAny]
    #     else:
    #         permission_classes = [IsRoleAdmin]
    #     return [permission() for permission in permission_classes]
    




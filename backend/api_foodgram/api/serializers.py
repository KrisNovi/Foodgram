from django.db import models
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from djoser.serializers import UserSerializer, UserCreateSerializer

from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient
from users.models import User
import base64
import webcolors


class UserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" не разрешено.'
            )
        return value


class UserSerializer(UserSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        extra_kwargs = {
            'slug': {
                'validators': [
                    UniqueValidator(
                        queryset=Tag.objects.all(),
                        message='Такой слаг уже существует'
                    )
                ]
            }
        }


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = (
            'amount',
            'recipe',
            'ingredient',
        )


class RecipeSerializerPost(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )


class RecipeSerializerGet(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField(read_only=True)
    # is_favorited = serializers.BooleanField()
    # is_in_shopping_cart = serializers.BooleanField()
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    # def get_tags(self, obj):
    #     tags = Tag.objects.filter(tag)
    



# class Base64ImageField(serializers.ImageField):
#     def to_internal_value(self, data):
#         # Если полученный объект строка, и эта строка 
#         # начинается с 'data:image'...
#         if isinstance(data, str) and data.startswith('data:image'):
#             # ...начинаем декодировать изображение из base64.
#             # Сначала нужно разделить строку на части.
#             format, imgstr = data.split(';base64,')  
#             # И извлечь расширение файла.
#             ext = format.split('/')[-1]  
#             # Затем декодировать сами данные и поместить результат в файл,
#             # которому дать название по шаблону.
#             data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

#         return super().to_internal_value(data)
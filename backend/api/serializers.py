from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredients, IngredientsInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Subscription

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed',
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user

        return (
            not user.is_anonymous
            and user.subscriber.filter(author=obj).exists()
        )


class UserCreateSerializer(UserCreateSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredients


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name')
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit',
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientsInRecipe


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class SubscribeSerializer(UserSerializer):
    recipes_count = serializers.IntegerField()
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes',
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        recipes_limit = self.context.get(
            'request').query_params.get('recipes_limit')
        if recipes_limit:
            if not recipes_limit.isdigit():
                raise serializers.ValidationError(
                    'Укажите числовое значение'
                )
            recipes_limit = int(recipes_limit)
            if recipes_limit < 0:
                raise serializers.ValidationError(
                    'Значение должно быть положительным'
                )

        serializer = ShortRecipeSerializer(
            obj.recipe.all()[:recipes_limit],
            many=True,
        )

        return serializer.data


class SubscribeSerializerPost(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'

    def validate(self, data):
        request = self.context.get('request')
        if data.get('user') == data.get('author'):
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        subs_exist = Subscription.objects.filter(**data).exists()
        if request.method == 'DELETE':
            if not subs_exist:
                raise serializers.ValidationError(
                    'Такой подписки не существует'
                )
        if request.method == 'POST':
            if subs_exist:
                raise serializers.ValidationError(
                    'Подписка была создана ранее.'
                )
        return data


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='ingredientsinrecipe_set',
    )
    image = serializers.SerializerMethodField(
        method_name='get_image_url',
    )
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_image_url(self, obj):
        return obj.image.url


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Ingredients.objects.all()
    )

    class Meta:
        fields = ('id', 'amount')
        model = IngredientsInRecipe


class RecipeSerializerPost(serializers.ModelSerializer):
    ingredients = IngredientsInRecipeSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

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
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        cooking_time = data.get('cooking_time')
        if len(ingredients) == 0:
            raise serializers.ValidationError(
                'Ингредиенты не выбраны.'
            )
        set_ingredients = set()
        for ingredient in ingredients:
            ingredient = ingredient.get('id')
            if ingredient in set_ingredients:
                raise serializers.ValidationError(
                    'Этот ингредиент уже выбран.'
                )
            set_ingredients.add(ingredient)
        if len(tags) == 0:
            raise serializers.ValidationError('Выберите тэги')

        for tag in tags:
            if tag not in Tag.objects.all():
                raise serializers.ValidationError(
                    'Несуществующий тэг'
                )
        if cooking_time <= 0:
            raise serializers.ValidationError(
                'Значение должно быть положительным!'
            )
        return data

    def add_ingredients(self, instance, ingredients_data):
        through_instances = []
        for ingredients in ingredients_data:
            ingridient, amount = ingredients.values()
            through_instance = IngredientsInRecipe(
                recipe=instance,
                ingredients=ingridient,
                amount=amount,
            )
            through_instances.append(through_instance)
        IngredientsInRecipe.objects.bulk_create(through_instances)
        return instance

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        instance = super().create(validated_data)
        return self.add_ingredients(instance, ingredients_data)

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        instance.ingredients.clear()
        self.add_ingredients(
            instance, ingredients_data
        )
        instance.save()
        return instance


class FavoriteBaseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    recipes = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
    )

    def favorite_validator(self, data, model):
        request = self.context.get('request')
        recipes = data.get('recipes')
        favorite_exist = request.user.fav.filter(recipes=recipes).exists()
        if request.method == 'DELETE':
            if not favorite_exist:
                raise serializers.ValidationError(
                    'Рецепта нет в избранном'
                )
        if request.method == 'POST':
            if favorite_exist:
                raise serializers.ValidationError(
                    'Рецепт уже есть в избранном'
                )
        return data

    def cart_validator(self, data, model):
        request = self.context.get('request')
        recipes = data.get('recipes')
        favorite_exist = request.user.cart.filter(recipes=recipes).exists()
        if request.method == 'DELETE':
            if not favorite_exist:
                raise serializers.ValidationError(
                    'Рецепта нет в корзине'
                )
        if request.method == 'POST':
            if favorite_exist:
                raise serializers.ValidationError(
                    'Рецепт уже есть в корзине'
                )
        return data

    def to_representation(self, instance):
        serializer = ShortRecipeSerializer(
            instance.recipes,
        )

        return serializer.data


class FavoriteSerializer(FavoriteBaseSerializer):

    class Meta:
        fields = '__all__'
        model = Favorite

    def validate(self, data):
        return self.favorite_validator(data, Favorite)


class ShoppingCartSerializer(FavoriteBaseSerializer):

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def validate(self, data):
        return self.cart_validator(data, ShoppingCart)

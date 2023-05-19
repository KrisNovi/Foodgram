from django.db import models
from django.http import HttpResponse
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        unique=True
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет',
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Слаг',
        unique=True
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингридиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ('-name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='tags',
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингредиенты',
        through='IngredientsInRecipe',
        related_name='ingredients',
    )
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (минуты)'
    )
    publication_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-publication_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        null=True,
        on_delete=models.CASCADE
    )
    ingredients = models.ForeignKey(
        Ingredients,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )

    def __str__(self):
        return f'{self.ingredients} в "{self.recipe}"'

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredients'),
                name='unique_recipe_ingredient'
            ),
        )


class FavoriteBaseModel(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.username


class Favorite(FavoriteBaseModel):

    class Meta:
        ordering = ('-user',)
        verbose_name = 'Избраный рецепт'
        verbose_name_plural = 'Избраные рецепты'


class ShoppingCart(FavoriteBaseModel):

    def download(self):
        ingredients = IngredientsInRecipe.objects.filter(recipe__in=self.recipes.all()).values('ingredients__name', 'ingredients__measurement_unit').annotate(total=models.Sum('amount'))

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'

        for ingredient in ingredients:
            response.write('{} - {}\n'.format(ingredient['ingredients__name'], ingredient['total']))

        return response

    class Meta:
        ordering = ('-user',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

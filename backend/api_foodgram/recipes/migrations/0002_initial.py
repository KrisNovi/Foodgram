# Generated by Django 3.2 on 2023-05-14 19:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='ingredients', through='recipes.IngredientsInRecipe', to='recipes.Ingredients', verbose_name='Ингредиенты'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='tags', to='recipes.Tag', verbose_name='Тэги'),
        ),
        migrations.AddField(
            model_name='ingredientsinrecipe',
            name='ingredients',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredients', verbose_name='Ингредиенты'),
        ),
        migrations.AddField(
            model_name='ingredientsinrecipe',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
        migrations.AddConstraint(
            model_name='ingredients',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_ingredient'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='recipes',
            field=models.ManyToManyField(to='recipes.Recipe', verbose_name='Рецепты'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='cart',
            name='recipes',
            field=models.ManyToManyField(to='recipes.Recipe', verbose_name='Рецепты'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='ingredientsinrecipe',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredients'), name='unique_recipe_ingredient'),
        ),
    ]

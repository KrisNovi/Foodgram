# Generated by Django 3.2 on 2023-05-07 11:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0004_remove_ingredient_qty'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteRecipesBaseModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RenameModel(
            old_name='Follow',
            new_name='Subscription',
        ),
        migrations.AlterModelOptions(
            name='favorite',
            options={'verbose_name': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'verbose_name': 'Ингредиенты', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'verbose_name': 'Ингредиент в рецепте', 'verbose_name_plural': 'Ингредиенты в рецептах'},
        ),
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique_favorite_user_recipe',
        ),
        migrations.RemoveField(
            model_name='favorite',
            name='id',
        ),
        migrations.RemoveField(
            model_name='favorite',
            name='recipe',
        ),
        migrations.RemoveField(
            model_name='favorite',
            name='user',
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Название рецепта'),
        ),
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('favoriterecipesbasemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='recipes.favoriterecipesbasemodel')),
            ],
            options={
                'verbose_name': 'Список покупок',
            },
            bases=('recipes.favoriterecipesbasemodel',),
        ),
        migrations.AddField(
            model_name='favoriterecipesbasemodel',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
        migrations.AddField(
            model_name='favoriterecipesbasemodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='favorite',
            name='favoriterecipesbasemodel_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='recipes.favoriterecipesbasemodel'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='favoriterecipesbasemodel',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_favorite_user_recipe'),
        ),
    ]

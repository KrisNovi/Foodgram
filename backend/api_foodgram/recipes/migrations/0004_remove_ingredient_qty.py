# Generated by Django 3.2 on 2023-05-05 12:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20230503_1636'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='qty',
        ),
    ]

# Generated by Django 4.2.11 on 2024-05-11 18:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_remove_favorite_unique_favorite_recipe_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='recipe',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
            preserve_default=False,
        ),
    ]

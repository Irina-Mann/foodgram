from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from rest_framework.reverse import reverse
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.MAX_LTH
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.MAX_LTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.MAX_LTH,
        unique=True
    )
    slug = models.SlugField(
        'Slug',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        'Название',
        max_length=settings.MAX_LTH
    )
    image = models.ImageField(
        'Фотография к рецепту',
        upload_to='recipes/'
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                settings.COOK_TIME,
                f'Время не может быть меньше {settings.COOK_TIME}'
            )
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.pk})


class RecipeIngredients(models.Model):
    """Промежуточная модель для таблиц Recipe и Ingredient"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient_in_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты',
        related_name='recipeingredient'
    )
    amount = models.PositiveSmallIntegerField('Количество')

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Favorite(models.Model):
    """Список любимых рецептов пользователя"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
        related_name='favorite'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            ),
        )
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'


class ShoppingCart(models.Model):
    """Список покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe'
            ),
        )
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок'


class Link(models.Model):
    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        primary_key=True
    )
    original_url = models.URLField('Полная ссылка')
    short_link = models.CharField('Короткая ссылка',
                                  max_length=settings.MAX_LTH,
                                  unique=True
                                  )

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

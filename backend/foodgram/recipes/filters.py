from django_filters.rest_framework import FilterSet, filters
from users.models import User

from .models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )

    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter',
        field_name='favorite__author'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter',
        field_name='shopping__author'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def is_favorite_filter(self, queryset, name, value):
        return self.filter_from_kwargs(queryset, value, name)

    def is_in_shopping_cart_filter(self, queryset, name, value):
        return self.filter_from_kwargs(queryset, value, name)

    def filter_from_kwargs(self, queryset, value, name):
        if value and self.request.user.id:
            return queryset.filter(**{name: self.request.user})
        return queryset

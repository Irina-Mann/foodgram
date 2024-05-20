import random
import string

from django.conf import settings
from django.db.models import Exists, OuterRef, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Ingredient, Link, Recipe, RecipeIngredients,
                     ShoppingCart, Tag)
from .pagination import RecipePagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, LinkSerializer,
                          RecipeCUDSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer)
from .utils import shopping_txt


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение списка ингредиентов или отдельного ингредиента"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Работа с рецептами"""
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = RecipePagination

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от метода запроса"""
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCUDSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all().prefetch_related(
            'author', 'ingredients')
        if self.action in ['list', 'retrieve'] and user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(Favorite.objects.filter(
                    user_id=user.id,
                    recipe=OuterRef('pk'))),
                is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                    user_id=user.id,
                    recipe=OuterRef('pk')))
            )
        return queryset

    def perform_create(self, serializer):
        """Присваемваем автора при создании рецепта"""
        serializer.save(author=self.request.user)

    def favorite_or_shopping_mixin(self, request, pk, model):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response('Рецепт не найден',
                                status=status.HTTP_400_BAD_REQUEST)
            return self.add_to(model, user=user, recipe=recipe)
        else:
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response('Рецепт отсутствует',
                                status=status.HTTP_404_NOT_FOUND)
            return self.delete_from(model, user=user, recipe=recipe)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        return self.favorite_or_shopping_mixin(request, pk, Favorite)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.favorite_or_shopping_mixin(request, pk, ShoppingCart)

    def add_to(self, model, user, recipe):
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response('Рецепт уже добавлен',
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, recipe):
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Рецепт уже удален',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredients.objects.filter(
            recipe__shopping__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))
        return shopping_txt(ingredients)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choices(characters, k=4))
    return f"http://{settings.DOMEN}/s/" + short_url


class GetRecipeLink(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        link_obj, create = Link.objects.get_or_create(recipe=recipe)
        if create:
            link_obj.short_link = generate_short_url()
            link_obj.original_url = recipe.get_absolute_url()
            link_obj.save()
        serializer = LinkSerializer(link_obj)
        return Response(serializer.data)


def redirect_to_full_link(request, short_link):
    try:
        link_obj = Link.objects.get(
            short_link=f'http://{settings.DOMEN}/s/' + short_link
        )
        full_link = link_obj.original_url.replace('/api', '', 1)[:-1]
        return redirect(full_link)
    except Link.DoesNotExist:
        return HttpResponse('Link not found', status=404)

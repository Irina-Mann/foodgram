import random
import string

from django.db.models import Sum
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
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = RecipePagination

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от метода запроса"""
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCUDSerializer

    def perform_create(self, serializer):
        """Присваемваем автора при создании рецепта"""
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response(
                    'Рецепт не найден', status=status.HTTP_400_BAD_REQUEST
                )
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    'Рецепт уже в избранном',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response(
                    'Рецепт не найден',
                    status=status.HTTP_404_NOT_FOUND
                )
            obj = Favorite.objects.filter(user=user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                'Рецепт отсутствует в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        user = request.user
        if request.method == 'POST':
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response(
                    'Рецепт не найден', status=status.HTTP_400_BAD_REQUEST
                )
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    'Рецепт уже в списке покупок',
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response(
                    'Рецепт не найден',
                    status=status.HTTP_404_NOT_FOUND
                )
            obj = ShoppingCart.objects.filter(user=user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                'Рецепт отсутствует в списке покупок',
                status=status.HTTP_400_BAD_REQUEST
            )

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
    return "http://foodyam.zapto.org/s/" + short_url


class GetRecipeLink(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        link_obj, create = Link.objects.get_or_create(recipe=recipe)
        if create:
            link_obj.short_link = generate_short_url()
            link_obj.save()
        else:
            pass
        serializer = LinkSerializer(link_obj)
        return Response(serializer.data)


def redirect_to_full_link(request, short_link):
    try:
        link_obj = Link.objects.get(
            short_link='http://foodyam.zapto.org/s/' + short_link
        )
        full_link = link_obj.original_url.replace('/api', '', 1)
        return redirect(full_link)
    except Link.DoesNotExist:
        return HttpResponse('Link not found', status=404)

from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from recipes.views import (GetRecipeLink, IngredientViewSet, RecipeViewSet,
                           TagViewSet)

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('recipes/<int:recipe_id>/get-link/', GetRecipeLink.as_view()),
    path('', include(router.urls)),
]

from django.conf.urls import include
from django.urls import path
from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from rest_framework.routers import DefaultRouter

from .views import GetRecipeLink

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('recipes/<int:recipe_id>/get-link/', GetRecipeLink.as_view()),
    path("", include(router.urls)),
]

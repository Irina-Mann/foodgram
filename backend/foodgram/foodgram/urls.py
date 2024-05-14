from django.contrib import admin
from django.urls import include, path
from recipes.views import redirect_to_full_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('recipes.urls')),
    path('s/<str:short_link>/', redirect_to_full_link),
]

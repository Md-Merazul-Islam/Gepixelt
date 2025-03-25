from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.http import HttpResponse
from django.urls import re_path


def favicon(request):
    return HttpResponse(status=204)


# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Gepixelt REST API",
        default_version='v1',
        description="API docs",
    ),
    public=True,
    permission_classes=[AllowAny],
)


def home(request):
    return JsonResponse({"message": "Welcome to the Gepixelt  REST API!"})


urlpatterns = [
    path("", home),
    re_path(r'^favicon.ico$', favicon),
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('auth/', include('auths.urls')),
        path('products/', include('products.urls')),
        path('payment/', include('payments.urls')),
        path('orders/', include('orders.urls')),
        
        

    ])),
    # Swagger Docs
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-ui'),
]

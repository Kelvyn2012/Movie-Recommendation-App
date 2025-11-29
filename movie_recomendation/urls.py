"""
URL configuration for movie_recomendation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Movie Recommendation API",
        default_version='v1',
        description="""
# Movie Recommendation API

A high-performance movie recommendation backend with enterprise-level features.

## Features

- User authentication with JWT
- Movie data from TMDb API
- Personalized recommendations
- Favorites and watchlist management
- Movie ratings and reviews
- Advanced caching with Redis
- Full-text movie search

## Authentication

This API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. Register a new account at `/api/auth/register/`
2. Login at `/api/auth/login/` to receive access and refresh tokens
3. Include the access token in the Authorization header: `Bearer <your-token>`

## Rate Limiting

- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Authentication endpoints: 5 requests/minute
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@movieapi.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/auth/', include('users.urls')),
    path('api/movies/', include('movies.urls')),
    path('api/users/favorites/', include(('movies.urls', 'favorites'), namespace='favorites')),
    path('api/users/ratings/', include(('movies.urls', 'ratings'), namespace='ratings')),
    path('api/users/watchlist/', include(('movies.urls', 'watchlist'), namespace='watchlist')),

    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/docs/json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

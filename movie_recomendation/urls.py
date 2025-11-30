from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse



def home(request):
    return HttpResponse("""
        <h1>Movie Recommendation API</h1>
        <p><a href="/api/docs/">API Documentation</a></p>
        <p><a href="/admin/">Admin Panel</a></p>
    """)

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

from movies import urls as movies_urls

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/auth/', include('users.urls')),
    path('api/movies/', include('movies.urls')),
    path('api/users/favorites/', include(movies_urls.favorites_urlpatterns)),
    path('api/users/ratings/', include(movies_urls.ratings_urlpatterns)),
    path('api/users/watchlist/', include(movies_urls.watchlist_urlpatterns)),

    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/docs/json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

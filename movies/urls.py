from django.urls import path
from .views import (
    TrendingMoviesView,
    MovieDetailView,
    MovieSearchView,
    RecommendedMoviesView,
    FavoriteMoviesListView,
    FavoriteMovieDeleteView,
    UserRatingListCreateView,
    WatchlistView,
    WatchlistDeleteView,
    PopularMoviesView,
    GenresView,
    HealthCheckView,
)

app_name = 'movies'

urlpatterns = [
    path('trending/', TrendingMoviesView.as_view(), name='trending'),
    path('popular/', PopularMoviesView.as_view(), name='popular'),
    path('recommended/', RecommendedMoviesView.as_view(), name='recommended'),
    path('search/', MovieSearchView.as_view(), name='search'),
    path('<int:id>/', MovieDetailView.as_view(), name='detail'),
    path('genres/', GenresView.as_view(), name='genres'),
    path('health/', HealthCheckView.as_view(), name='health'),
]

favorites_urlpatterns = [
    path('', FavoriteMoviesListView.as_view(), name='favorites'),
    path('<int:id>/', FavoriteMovieDeleteView.as_view(), name='favorite_delete'),
]

ratings_urlpatterns = [
    path('', UserRatingListCreateView.as_view(), name='ratings'),
]

watchlist_urlpatterns = [
    path('', WatchlistView.as_view(), name='watchlist'),
    path('<int:id>/', WatchlistDeleteView.as_view(), name='watchlist_delete'),
]

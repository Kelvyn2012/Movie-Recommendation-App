from django.contrib import admin
from .models import Movie, FavoriteMovie, UserRating, Watchlist


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'tmdb_id', 'release_date', 'vote_average', 'popularity', 'created_at']
    list_filter = ['release_date', 'adult', 'original_language']
    search_fields = ['title', 'original_title', 'tmdb_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-popularity', '-vote_average']


@admin.register(FavoriteMovie)
class FavoriteMovieAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'tmdb_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'user__username', 'movie__title']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'movie']


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'rating', 'created_at', 'updated_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__email', 'user__username', 'movie__title']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'movie']


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'tmdb_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'user__username', 'movie__title']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'movie']

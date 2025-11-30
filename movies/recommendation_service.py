import logging
from typing import List, Dict
from django.core.cache import cache
from django.conf import settings
from django.db.models import Avg, Count, Q
from .models import Movie, FavoriteMovie, UserRating
from .tmdb_service import tmdb_service
from .utils import batch_create_movies_from_tmdb

logger = logging.getLogger(__name__)


class RecommendationService:
    def __init__(self, user):
        self.user = user

    def get_personalized_recommendations(self, limit: int = 20) -> List[Movie]:
        cache_key = f'recommendations_user_{self.user.id}'
        cached_recommendations = cache.get(cache_key)

        if cached_recommendations:
            logger.info(f"Returning cached recommendations for user {self.user.id}")
            return cached_recommendations

        recommendations = self._generate_recommendations(limit)

        cache.set(cache_key, recommendations, settings.CACHE_TTL['RECOMMENDATIONS'])
        logger.info(f"Cached recommendations for user {self.user.id}")

        return recommendations

    def _generate_recommendations(self, limit: int) -> List[Movie]:
        favorite_movies = FavoriteMovie.objects.filter(user=self.user).select_related('movie')
        user_ratings = UserRating.objects.filter(user=self.user, rating__gte=7).select_related('movie')

        if not favorite_movies.exists() and not user_ratings.exists():
            return self._get_popular_movies(limit)

        favorite_genres = self._get_favorite_genres(favorite_movies, user_ratings)

        if not favorite_genres:
            return self._get_popular_movies(limit)

        recommended_movies = self._get_movies_by_genres(favorite_genres, limit)

        if len(recommended_movies) < limit:
            additional_movies = self._get_popular_movies(limit - len(recommended_movies))
            recommended_movies.extend(additional_movies)

        return recommended_movies[:limit]

    def _get_favorite_genres(self, favorite_movies, user_ratings) -> List[int]:
        genre_count = {}

        for favorite in favorite_movies:
            for genre in favorite.movie.genres:
                genre_id = genre.get('id')
                if genre_id:
                    genre_count[genre_id] = genre_count.get(genre_id, 0) + 2

        for rating in user_ratings:
            for genre in rating.movie.genres:
                genre_id = genre.get('id')
                if genre_id:
                    genre_count[genre_id] = genre_count.get(genre_id, 0) + 1

        sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
        return [genre_id for genre_id, _ in sorted_genres[:3]]

    def _get_movies_by_genres(self, genre_ids: List[int], limit: int) -> List[Movie]:
        exclude_movie_ids = list(
            FavoriteMovie.objects.filter(user=self.user).values_list('movie_id', flat=True)
        )

        # Filter movies that have any of the favorite genres
        # Since SQLite doesn't support JSON contains, we filter in Python
        all_movies = Movie.objects.exclude(id__in=exclude_movie_ids).order_by('-vote_average', '-popularity')

        matching_movies = []
        for movie in all_movies:
            if any(genre.get('id') in genre_ids for genre in movie.genres if isinstance(genre, dict)):
                matching_movies.append(movie)
                if len(matching_movies) >= limit:
                    break

        if len(matching_movies) < limit // 2:
            tmdb_results = tmdb_service.discover_movies(
                **{
                    'with_genres': ','.join(map(str, genre_ids)),
                    'sort_by': 'vote_average.desc',
                    'vote_count.gte': 100,
                    'page': 1
                }
            )

            if tmdb_results and tmdb_results.get('results'):
                tmdb_movies = batch_create_movies_from_tmdb(tmdb_results['results'])
                matching_movies = list(matching_movies) + tmdb_movies

        return matching_movies[:limit]

    def _get_popular_movies(self, limit: int) -> List[Movie]:
        movies = Movie.objects.order_by('-popularity', '-vote_average')[:limit]

        if movies.count() < limit:
            tmdb_results = tmdb_service.get_popular_movies(page=1)
            if tmdb_results and tmdb_results.get('results'):
                tmdb_movies = batch_create_movies_from_tmdb(tmdb_results['results'])
                movies = list(movies) + tmdb_movies

        return list(movies)[:limit]

    def get_similar_movies(self, movie_id: int, limit: int = 10) -> List[Movie]:
        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            logger.error(f"Movie with ID {movie_id} not found")
            return []

        cache_key = f'similar_movies_{movie.tmdb_id}'
        cached_similar = cache.get(cache_key)

        if cached_similar:
            return cached_similar

        tmdb_details = tmdb_service.get_movie_details(movie.tmdb_id)
        if not tmdb_details:
            return []

        similar_movies_data = tmdb_details.get('similar', {}).get('results', [])
        if similar_movies_data:
            similar_movies = batch_create_movies_from_tmdb(similar_movies_data[:limit])
        else:
            similar_movies = []

        cache.set(cache_key, similar_movies, settings.CACHE_TTL['MOVIE_DETAILS'])

        return similar_movies


def get_collaborative_filtering_recommendations(user, limit: int = 20) -> List[Movie]:
    user_favorites = set(
        FavoriteMovie.objects.filter(user=user).values_list('movie_id', flat=True)
    )

    if not user_favorites:
        return []

    similar_users = FavoriteMovie.objects.filter(
        movie_id__in=user_favorites
    ).exclude(
        user=user
    ).values('user').annotate(
        common_favorites=Count('id')
    ).order_by('-common_favorites')[:10]

    similar_user_ids = [item['user'] for item in similar_users]

    recommended_movies = FavoriteMovie.objects.filter(
        user_id__in=similar_user_ids
    ).exclude(
        movie_id__in=user_favorites
    ).values('movie').annotate(
        recommendation_score=Count('id')
    ).order_by('-recommendation_score')[:limit]

    movie_ids = [item['movie'] for item in recommended_movies]
    movies = Movie.objects.filter(id__in=movie_ids)

    return list(movies)

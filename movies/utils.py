import logging
from datetime import datetime
from typing import Optional
from .models import Movie
from .tmdb_service import tmdb_service

logger = logging.getLogger(__name__)


def get_or_create_movie_from_tmdb(tmdb_id: int) -> Optional[Movie]:
    try:
        return Movie.objects.get(tmdb_id=tmdb_id)
    except Movie.DoesNotExist:
        movie_data = tmdb_service.get_movie_details(tmdb_id)
        if not movie_data:
            logger.error(f"Failed to fetch movie data for TMDb ID: {tmdb_id}")
            return None

        return create_movie_from_tmdb_data(movie_data)


def create_movie_from_tmdb_data(movie_data: dict) -> Movie:
    release_date = None
    if movie_data.get('release_date'):
        try:
            release_date = datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid release date format: {movie_data.get('release_date')}")

    genres = [{'id': g['id'], 'name': g['name']} for g in movie_data.get('genres', [])]

    movie, created = Movie.objects.update_or_create(
        tmdb_id=movie_data['id'],
        defaults={
            'title': movie_data.get('title', ''),
            'original_title': movie_data.get('original_title', ''),
            'overview': movie_data.get('overview', ''),
            'poster_path': movie_data.get('poster_path', ''),
            'backdrop_path': movie_data.get('backdrop_path', ''),
            'release_date': release_date,
            'runtime': movie_data.get('runtime'),
            'vote_average': movie_data.get('vote_average', 0.0),
            'vote_count': movie_data.get('vote_count', 0),
            'popularity': movie_data.get('popularity', 0.0),
            'genres': genres,
            'original_language': movie_data.get('original_language', ''),
            'adult': movie_data.get('adult', False),
        }
    )

    action = "Created" if created else "Updated"
    logger.info(f"{action} movie: {movie.title} (TMDb ID: {movie.tmdb_id})")

    return movie


def batch_create_movies_from_tmdb(movie_list: list) -> list:
    movies = []
    for movie_data in movie_list:
        release_date = None
        if movie_data.get('release_date'):
            try:
                release_date = datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date()
            except ValueError:
                pass

        # TMDb returns genre_ids as a list of integers in trending/search results
        genre_ids = movie_data.get('genre_ids', [])
        if genre_ids and isinstance(genre_ids[0], int):
            genres = [{'id': gid} for gid in genre_ids]
        else:
            genres = [{'id': g['id'], 'name': g.get('name', '')} for g in genre_ids]

        movie, _ = Movie.objects.update_or_create(
            tmdb_id=movie_data['id'],
            defaults={
                'title': movie_data.get('title', ''),
                'original_title': movie_data.get('original_title', ''),
                'overview': movie_data.get('overview', ''),
                'poster_path': movie_data.get('poster_path', ''),
                'backdrop_path': movie_data.get('backdrop_path', ''),
                'release_date': release_date,
                'vote_average': movie_data.get('vote_average', 0.0),
                'vote_count': movie_data.get('vote_count', 0),
                'popularity': movie_data.get('popularity', 0.0),
                'genres': genres,
                'original_language': movie_data.get('original_language', ''),
                'adult': movie_data.get('adult', False),
            }
        )
        movies.append(movie)

    return movies

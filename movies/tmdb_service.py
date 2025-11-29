import requests
import logging
from typing import Dict, List, Optional
from django.conf import settings
from django.core.cache import cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class TMDbService:
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.image_base_url = settings.TMDB_IMAGE_BASE_URL
        self.session = self._create_session()

    def _create_session(self):
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        if not self.api_key:
            logger.error("TMDb API key is not configured")
            return None

        if params is None:
            params = {}

        params['api_key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDb API request failed: {str(e)}")
            return None

    def get_trending_movies(self, time_window: str = 'week', page: int = 1) -> Optional[Dict]:
        cache_key = f'trending_movies_{time_window}_{page}'
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info(f"Returning cached trending movies for {time_window}")
            return cached_data

        endpoint = f'trending/movie/{time_window}'
        data = self._make_request(endpoint, {'page': page})

        if data:
            cache.set(cache_key, data, settings.CACHE_TTL['TRENDING_MOVIES'])
            logger.info(f"Cached trending movies for {time_window}")

        return data

    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        cache_key = f'movie_details_{movie_id}'
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info(f"Returning cached movie details for {movie_id}")
            return cached_data

        endpoint = f'movie/{movie_id}'
        params = {
            'append_to_response': 'credits,videos,similar,recommendations'
        }
        data = self._make_request(endpoint, params)

        if data:
            cache.set(cache_key, data, settings.CACHE_TTL['MOVIE_DETAILS'])
            logger.info(f"Cached movie details for {movie_id}")

        return data

    def search_movies(self, query: str, page: int = 1) -> Optional[Dict]:
        cache_key = f'search_movies_{query}_{page}'
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info(f"Returning cached search results for '{query}'")
            return cached_data

        endpoint = 'search/movie'
        params = {
            'query': query,
            'page': page,
            'include_adult': False
        }
        data = self._make_request(endpoint, params)

        if data:
            cache.set(cache_key, data, settings.CACHE_TTL['SEARCH_RESULTS'])
            logger.info(f"Cached search results for '{query}'")

        return data

    def get_popular_movies(self, page: int = 1) -> Optional[Dict]:
        cache_key = f'popular_movies_{page}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        endpoint = 'movie/popular'
        data = self._make_request(endpoint, {'page': page})

        if data:
            cache.set(cache_key, data, settings.CACHE_TTL['TRENDING_MOVIES'])

        return data

    def get_top_rated_movies(self, page: int = 1) -> Optional[Dict]:
        cache_key = f'top_rated_movies_{page}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        endpoint = 'movie/top_rated'
        data = self._make_request(endpoint, {'page': page})

        if data:
            cache.set(cache_key, data, settings.CACHE_TTL['TRENDING_MOVIES'])

        return data

    def get_movie_genres(self) -> Optional[Dict]:
        cache_key = 'movie_genres'
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        endpoint = 'genre/movie/list'
        data = self._make_request(endpoint)

        if data:
            cache.set(cache_key, data, 86400 * 7)  # Cache for 7 days

        return data

    def discover_movies(self, **kwargs) -> Optional[Dict]:
        endpoint = 'discover/movie'
        data = self._make_request(endpoint, kwargs)
        return data

    def get_image_url(self, path: str, size: str = 'w500') -> str:
        if not path:
            return ''
        return f"{self.image_base_url}{size}{path}"


tmdb_service = TMDbService()

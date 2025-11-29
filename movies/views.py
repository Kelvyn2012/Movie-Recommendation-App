from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Movie, FavoriteMovie, UserRating, Watchlist
from .serializers import (
    MovieSerializer,
    MovieDetailSerializer,
    FavoriteMovieSerializer,
    UserRatingSerializer,
    WatchlistSerializer
)
from .tmdb_service import tmdb_service
from .utils import batch_create_movies_from_tmdb, get_or_create_movie_from_tmdb
from .recommendation_service import RecommendationService, get_collaborative_filtering_recommendations


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TrendingMoviesView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = MovieSerializer
    pagination_class = StandardPagination

    @swagger_auto_schema(
        operation_description="Get trending movies from TMDb",
        manual_parameters=[
            openapi.Parameter('time_window', openapi.IN_QUERY, description="Time window: 'day' or 'week'", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
        ],
        responses={200: MovieSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        time_window = request.query_params.get('time_window', 'week')
        page = int(request.query_params.get('page', 1))

        cache_key = f'trending_movies_{time_window}_{page}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        tmdb_data = tmdb_service.get_trending_movies(time_window=time_window, page=page)

        if not tmdb_data:
            return Response(
                {'error': 'Failed to fetch trending movies'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        movies = batch_create_movies_from_tmdb(tmdb_data.get('results', []))
        serializer = self.get_serializer(movies, many=True, context={'request': request})

        response_data = {
            'count': tmdb_data.get('total_results', 0),
            'page': tmdb_data.get('page', 1),
            'total_pages': tmdb_data.get('total_pages', 1),
            'results': serializer.data
        }

        cache.set(cache_key, response_data, settings.CACHE_TTL['TRENDING_MOVIES'])

        return Response(response_data)


class MovieDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = MovieDetailSerializer
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_description="Get detailed information about a specific movie",
        responses={
            200: MovieDetailSerializer,
            404: 'Movie not found'
        }
    )
    def get(self, request, *args, **kwargs):
        movie_id = kwargs.get('id')

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {'error': 'Movie not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(movie, context={'request': request})
        return Response(serializer.data)


class MovieSearchView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = MovieSerializer
    pagination_class = StandardPagination

    @swagger_auto_schema(
        operation_description="Search for movies by title, genre, or keywords",
        manual_parameters=[
            openapi.Parameter('query', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
        ],
        responses={200: MovieSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', '')
        page = int(request.query_params.get('page', 1))

        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f'search_movies_{query}_{page}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        tmdb_data = tmdb_service.search_movies(query=query, page=page)

        if not tmdb_data:
            return Response(
                {'error': 'Failed to search movies'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        movies = batch_create_movies_from_tmdb(tmdb_data.get('results', []))
        serializer = self.get_serializer(movies, many=True, context={'request': request})

        response_data = {
            'count': tmdb_data.get('total_results', 0),
            'page': tmdb_data.get('page', 1),
            'total_pages': tmdb_data.get('total_pages', 1),
            'results': serializer.data
        }

        cache.set(cache_key, response_data, settings.CACHE_TTL['SEARCH_RESULTS'])

        return Response(response_data)


class RecommendedMoviesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MovieSerializer
    pagination_class = StandardPagination

    @swagger_auto_schema(
        operation_description="Get personalized movie recommendations based on user preferences and favorites",
        responses={200: MovieSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        recommendation_service = RecommendationService(request.user)
        recommended_movies = recommendation_service.get_personalized_recommendations(limit=40)

        collaborative_movies = get_collaborative_filtering_recommendations(request.user, limit=20)

        all_recommendations = list(set(recommended_movies + collaborative_movies))

        page = self.paginate_queryset(all_recommendations)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(all_recommendations, many=True, context={'request': request})
        return Response(serializer.data)


class FavoriteMoviesListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteMovieSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return FavoriteMovie.objects.filter(user=self.request.user).select_related('movie')

    @swagger_auto_schema(
        operation_description="Get user's favorite movies",
        responses={200: FavoriteMovieSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Add a movie to favorites",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['tmdb_id'],
            properties={
                'tmdb_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='TMDb movie ID'),
            },
        ),
        responses={
            201: FavoriteMovieSerializer,
            400: 'Bad Request'
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavoriteMovieDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return FavoriteMovie.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Remove a movie from favorites",
        responses={
            204: 'Successfully deleted',
            404: 'Movie not found in favorites'
        }
    )
    def delete(self, request, *args, **kwargs):
        try:
            favorite = self.get_queryset().get(id=kwargs.get('id'))
            favorite.delete()
            return Response(
                {'message': 'Movie removed from favorites'},
                status=status.HTTP_204_NO_CONTENT
            )
        except FavoriteMovie.DoesNotExist:
            return Response(
                {'error': 'Movie not found in favorites'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserRatingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserRatingSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return UserRating.objects.filter(user=self.request.user).select_related('movie')

    @swagger_auto_schema(
        operation_description="Get user's movie ratings",
        responses={200: UserRatingSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Rate a movie",
        request_body=UserRatingSerializer,
        responses={
            201: UserRatingSerializer,
            400: 'Bad Request'
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WatchlistView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WatchlistSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).select_related('movie')

    @swagger_auto_schema(
        operation_description="Get user's watchlist",
        responses={200: WatchlistSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Add a movie to watchlist",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['tmdb_id'],
            properties={
                'tmdb_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='TMDb movie ID'),
            },
        ),
        responses={
            201: WatchlistSerializer,
            400: 'Bad Request'
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WatchlistDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Remove a movie from watchlist",
        responses={
            204: 'Successfully deleted',
            404: 'Movie not found in watchlist'
        }
    )
    def delete(self, request, *args, **kwargs):
        try:
            watchlist_item = self.get_queryset().get(id=kwargs.get('id'))
            watchlist_item.delete()
            return Response(
                {'message': 'Movie removed from watchlist'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Watchlist.DoesNotExist:
            return Response(
                {'error': 'Movie not found in watchlist'},
                status=status.HTTP_404_NOT_FOUND
            )


class PopularMoviesView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = MovieSerializer
    pagination_class = StandardPagination

    @swagger_auto_schema(
        operation_description="Get popular movies",
        responses={200: MovieSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        page = int(request.query_params.get('page', 1))
        tmdb_data = tmdb_service.get_popular_movies(page=page)

        if not tmdb_data:
            return Response(
                {'error': 'Failed to fetch popular movies'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        movies = batch_create_movies_from_tmdb(tmdb_data.get('results', []))
        serializer = self.get_serializer(movies, many=True, context={'request': request})

        return Response({
            'count': tmdb_data.get('total_results', 0),
            'page': tmdb_data.get('page', 1),
            'total_pages': tmdb_data.get('total_pages', 1),
            'results': serializer.data
        })


class GenresView(views.APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get list of all movie genres",
        responses={200: openapi.Response('List of genres')}
    )
    def get(self, request):
        genres_data = tmdb_service.get_movie_genres()

        if not genres_data:
            return Response(
                {'error': 'Failed to fetch genres'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response(genres_data)


class HealthCheckView(views.APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Health check endpoint",
        responses={200: openapi.Response('Service is healthy')}
    )
    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'Movie Recommendation API',
            'version': '1.0.0'
        })

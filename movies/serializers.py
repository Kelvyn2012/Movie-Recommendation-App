from rest_framework import serializers
from .models import Movie, FavoriteMovie, UserRating, Watchlist


class MovieSerializer(serializers.ModelSerializer):
    poster_url = serializers.SerializerMethodField()
    backdrop_url = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            'id', 'tmdb_id', 'title', 'original_title', 'overview',
            'poster_path', 'poster_url', 'backdrop_path', 'backdrop_url',
            'release_date', 'runtime', 'vote_average', 'vote_count',
            'popularity', 'genres', 'original_language', 'adult',
            'created_at', 'updated_at', 'is_favorite', 'user_rating'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_poster_url(self, obj):
        from .tmdb_service import tmdb_service
        return tmdb_service.get_image_url(obj.poster_path)

    def get_backdrop_url(self, obj):
        from .tmdb_service import tmdb_service
        return tmdb_service.get_image_url(obj.backdrop_path, 'w1280')

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavoriteMovie.objects.filter(user=request.user, movie=obj).exists()
        return False

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rating = UserRating.objects.filter(user=request.user, movie=obj).first()
            if rating:
                return {'rating': rating.rating, 'review': rating.review}
        return None


class MovieDetailSerializer(MovieSerializer):
    similar_movies = serializers.SerializerMethodField()

    class Meta(MovieSerializer.Meta):
        fields = MovieSerializer.Meta.fields + ['similar_movies']

    def get_similar_movies(self, obj):
        return []


class FavoriteMovieSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    tmdb_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FavoriteMovie
        fields = ['id', 'movie', 'tmdb_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        from .utils import get_or_create_movie_from_tmdb

        tmdb_id = validated_data.pop('tmdb_id')
        user = self.context['request'].user

        movie = get_or_create_movie_from_tmdb(tmdb_id)
        if not movie:
            raise serializers.ValidationError("Movie not found in TMDb")

        favorite, created = FavoriteMovie.objects.get_or_create(
            user=user,
            movie=movie,
            defaults={'tmdb_id': tmdb_id}
        )

        if not created:
            raise serializers.ValidationError("Movie already in favorites")

        return favorite


class UserRatingSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    tmdb_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = UserRating
        fields = ['id', 'movie', 'tmdb_id', 'rating', 'review', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        from .utils import get_or_create_movie_from_tmdb

        tmdb_id = validated_data.pop('tmdb_id')
        user = self.context['request'].user

        movie = get_or_create_movie_from_tmdb(tmdb_id)
        if not movie:
            raise serializers.ValidationError("Movie not found in TMDb")

        rating, created = UserRating.objects.update_or_create(
            user=user,
            movie=movie,
            defaults={
                'rating': validated_data.get('rating'),
                'review': validated_data.get('review', '')
            }
        )

        return rating


class WatchlistSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    tmdb_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Watchlist
        fields = ['id', 'movie', 'tmdb_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        from .utils import get_or_create_movie_from_tmdb

        tmdb_id = validated_data.pop('tmdb_id')
        user = self.context['request'].user

        movie = get_or_create_movie_from_tmdb(tmdb_id)
        if not movie:
            raise serializers.ValidationError("Movie not found in TMDb")

        watchlist_item, created = Watchlist.objects.get_or_create(
            user=user,
            movie=movie,
            defaults={'tmdb_id': tmdb_id}
        )

        if not created:
            raise serializers.ValidationError("Movie already in watchlist")

        return watchlist_item

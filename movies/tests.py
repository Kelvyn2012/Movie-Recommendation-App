import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from .models import Movie, FavoriteMovie, UserRating, Watchlist


@pytest.mark.django_db
class TestMovieAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.movie = Movie.objects.create(
            tmdb_id=12345,
            title='Test Movie',
            overview='A test movie',
            vote_average=8.5,
            popularity=100.0,
            release_date='2024-01-01'
        )

    def test_trending_movies_unauthenticated(self):
        url = reverse('movies:trending')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_movie_detail(self):
        url = reverse('movies:detail', kwargs={'id': self.movie.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Movie')

    def test_add_to_favorites_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('favorites:favorites')
        data = {'tmdb_id': self.movie.tmdb_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FavoriteMovie.objects.filter(user=self.user, movie=self.movie).exists())

    def test_add_to_favorites_unauthenticated(self):
        url = reverse('favorites:favorites')
        data = {'tmdb_id': self.movie.tmdb_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_favorites(self):
        self.client.force_authenticate(user=self.user)
        FavoriteMovie.objects.create(user=self.user, movie=self.movie, tmdb_id=self.movie.tmdb_id)

        url = reverse('favorites:favorites')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_rate_movie(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('ratings:ratings')
        data = {
            'tmdb_id': self.movie.tmdb_id,
            'rating': 9,
            'review': 'Great movie!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserRating.objects.filter(user=self.user, movie=self.movie).exists())

    def test_search_movies(self):
        url = reverse('movies:search')
        response = self.client.get(url, {'query': 'test'})
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])


@pytest.mark.django_db
class TestUserAPI(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        url = reverse('users:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login(self):
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        url = reverse('users:login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_get_profile_authenticated(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        url = reverse('users:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')


class TestRecommendationService(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.movie1 = Movie.objects.create(
            tmdb_id=1,
            title='Movie 1',
            genres=[{'id': 28, 'name': 'Action'}],
            vote_average=8.0,
            popularity=100.0
        )
        self.movie2 = Movie.objects.create(
            tmdb_id=2,
            title='Movie 2',
            genres=[{'id': 28, 'name': 'Action'}],
            vote_average=7.5,
            popularity=90.0
        )

    def test_recommendations_with_favorites(self):
        FavoriteMovie.objects.create(user=self.user, movie=self.movie1, tmdb_id=1)
        from .recommendation_service import RecommendationService
        service = RecommendationService(self.user)
        recommendations = service.get_personalized_recommendations(limit=10)
        self.assertIsInstance(recommendations, list)

# API Usage Examples

This document provides practical examples of how to use the Movie Recommendation API.

## Base URL

```
http://localhost:8000
```

## Authentication Flow

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "bio": "Movie enthusiast",
    "favorite_genres": ["Action", "Sci-Fi"]
  }'
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "bio": "Movie enthusiast",
    "favorite_genres": ["Action", "Sci-Fi"]
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "message": "User registered successfully"
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. Refresh Token

```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

### 4. Get User Profile

```bash
curl http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Movie Endpoints

### Get Trending Movies

```bash
# Trending this week (default)
curl http://localhost:8000/api/movies/trending/

# Trending today
curl http://localhost:8000/api/movies/trending/?time_window=day

# With pagination
curl http://localhost:8000/api/movies/trending/?page=2&page_size=10
```

**Response:**
```json
{
  "count": 1000,
  "page": 1,
  "total_pages": 50,
  "results": [
    {
      "id": 1,
      "tmdb_id": 550,
      "title": "Fight Club",
      "overview": "A ticking-time-bomb insomniac...",
      "poster_url": "https://image.tmdb.org/t/p/w500/...",
      "backdrop_url": "https://image.tmdb.org/t/p/w1280/...",
      "release_date": "1999-10-15",
      "vote_average": 8.4,
      "popularity": 123.45,
      "genres": [
        {"id": 18, "name": "Drama"}
      ]
    }
  ]
}
```

### Get Popular Movies

```bash
curl http://localhost:8000/api/movies/popular/
```

### Search Movies

```bash
curl "http://localhost:8000/api/movies/search/?query=inception"

# With pagination
curl "http://localhost:8000/api/movies/search/?query=matrix&page=1&page_size=20"
```

### Get Movie Details

```bash
curl http://localhost:8000/api/movies/123/
```

### Get All Genres

```bash
curl http://localhost:8000/api/movies/genres/
```

## Personalized Features (Authenticated)

### Get Personalized Recommendations

```bash
curl http://localhost:8000/api/movies/recommended/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Manage Favorites

#### Add to Favorites

```bash
curl -X POST http://localhost:8000/api/users/favorites/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tmdb_id": 550
  }'
```

**Response:**
```json
{
  "id": 1,
  "movie": {
    "id": 1,
    "tmdb_id": 550,
    "title": "Fight Club",
    "vote_average": 8.4
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Get Favorites

```bash
curl http://localhost:8000/api/users/favorites/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Remove from Favorites

```bash
curl -X DELETE http://localhost:8000/api/users/favorites/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Rate a Movie

```bash
curl -X POST http://localhost:8000/api/users/ratings/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tmdb_id": 550,
    "rating": 9,
    "review": "Absolutely mind-blowing! A masterpiece of cinema."
  }'
```

### Get User Ratings

```bash
curl http://localhost:8000/api/users/ratings/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Manage Watchlist

#### Add to Watchlist

```bash
curl -X POST http://localhost:8000/api/users/watchlist/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tmdb_id": 550
  }'
```

#### Get Watchlist

```bash
curl http://localhost:8000/api/users/watchlist/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Remove from Watchlist

```bash
curl -X DELETE http://localhost:8000/api/users/watchlist/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## User Preferences

### Get User Preferences

```bash
curl http://localhost:8000/api/auth/preferences/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Update Preferences

```bash
curl -X PUT http://localhost:8000/api/auth/preferences/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_genres": [28, 878, 12],
    "preferred_languages": ["en", "es"],
    "min_rating": 7.0
  }'
```

## Python Examples

### Using Requests Library

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
register_data = {
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
}
response = requests.post(f"{BASE_URL}/api/auth/register/", json=register_data)
tokens = response.json()
access_token = tokens['access']

# Get trending movies
headers = {"Authorization": f"Bearer {access_token}"}
trending = requests.get(f"{BASE_URL}/api/movies/trending/")
print(trending.json())

# Add to favorites
favorite_data = {"tmdb_id": 550}
response = requests.post(
    f"{BASE_URL}/api/users/favorites/",
    json=favorite_data,
    headers=headers
)

# Get personalized recommendations
recommendations = requests.get(
    f"{BASE_URL}/api/movies/recommended/",
    headers=headers
)
print(recommendations.json())
```

### Using JavaScript (Fetch API)

```javascript
const BASE_URL = 'http://localhost:8000';

// Register
async function register() {
  const response = await fetch(`${BASE_URL}/api/auth/register/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: 'johndoe',
      email: 'john@example.com',
      password: 'SecurePass123!',
      password2: 'SecurePass123!',
    }),
  });
  const data = await response.json();
  return data.access;
}

// Get trending movies
async function getTrending(token) {
  const response = await fetch(`${BASE_URL}/api/movies/trending/`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  return await response.json();
}

// Add to favorites
async function addFavorite(token, tmdbId) {
  const response = await fetch(`${BASE_URL}/api/users/favorites/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ tmdb_id: tmdbId }),
  });
  return await response.json();
}

// Usage
const token = await register();
const trending = await getTrending(token);
await addFavorite(token, 550);
```

## Common Response Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Resource deleted successfully
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `503 Service Unavailable` - TMDb API is unavailable

## Rate Limits

- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Authentication endpoints: 5 requests/minute

## Health Check

```bash
curl http://localhost:8000/api/movies/health/
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Movie Recommendation API",
  "version": "1.0.0"
}
```

## Tips

1. **Save your access token** - You'll need it for authenticated requests
2. **Use the Swagger UI** - Available at http://localhost:8000/api/docs/ for interactive testing
3. **Check response headers** - They include rate limit information
4. **Handle token expiration** - Refresh tokens when you get a 401 response
5. **Pagination** - Use `page` and `page_size` parameters for large result sets

For more details, visit the Swagger documentation at `/api/docs/`

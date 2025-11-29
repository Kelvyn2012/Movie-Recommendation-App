# Contributing to Movie Recommendation API

Thank you for your interest in contributing to the Movie Recommendation API! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Follow the project's coding standards

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/movie-recommendation-api.git
cd movie-recommendation-api
```

### 2. Set Up Development Environment

```bash
# Run the setup script
./setup.sh

# Or manually:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Run Tests

```bash
pytest
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `perf/` - Performance improvements
- `test/` - Test additions or modifications

### 2. Make Your Changes

Follow these guidelines:

#### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Use type hints where appropriate

#### Example:
```python
def calculate_recommendation_score(user: User, movie: Movie) -> float:
    """
    Calculate recommendation score for a user-movie pair.

    Args:
        user: The user object
        movie: The movie object

    Returns:
        Float score between 0 and 1
    """
    # Implementation
    pass
```

### 3. Write Tests

All new features must include tests:

```python
# movies/tests.py
def test_new_feature(self):
    """Test description"""
    # Arrange
    user = User.objects.create_user(...)

    # Act
    result = some_function(user)

    # Assert
    self.assertEqual(result, expected)
```

Run tests before committing:
```bash
pytest
coverage run -m pytest
coverage report
```

### 4. Commit Your Changes

Follow conventional commit messages:

```bash
git add .
git commit -m "feat: add collaborative filtering to recommendations

- Implement user similarity calculation
- Add weight-based recommendation scoring
- Include caching for similarity matrix
- Add tests for collaborative filtering"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `perf:` - Performance improvements
- `refactor:` - Code refactoring
- `style:` - Code style changes (formatting)
- `chore:` - Build/dependency updates

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Detailed description of what and why
- Link to related issues
- Screenshots (if UI changes)
- Test results

## Testing Guidelines

### Unit Tests

Test individual functions and methods:

```python
class TestTMDbService(TestCase):
    def test_get_trending_movies(self):
        service = TMDbService()
        result = service.get_trending_movies()
        self.assertIsNotNone(result)
```

### Integration Tests

Test API endpoints:

```python
class TestMovieAPI(TestCase):
    def test_trending_endpoint(self):
        response = self.client.get('/api/movies/trending/')
        self.assertEqual(response.status_code, 200)
```

### Coverage Requirements

- Maintain minimum 80% code coverage
- All new features must have tests
- Bug fixes should include regression tests

## Documentation

### Code Documentation

Add docstrings to all:
- Classes
- Functions
- Complex algorithms

### API Documentation

Update Swagger documentation:

```python
@swagger_auto_schema(
    operation_description="Detailed description",
    responses={
        200: ResponseSerializer,
        400: 'Bad Request'
    }
)
def my_view(request):
    pass
```

### README Updates

Update README.md if you:
- Add new features
- Change setup process
- Modify API endpoints
- Update dependencies

## Performance Guidelines

### Database Queries

Optimize database access:

```python
# Good
movies = Movie.objects.select_related('user').prefetch_related('genres')

# Bad
for movie in Movie.objects.all():
    print(movie.user.name)  # N+1 query problem
```

### Caching

Use caching for expensive operations:

```python
cache_key = f'recommendations_{user.id}'
cached = cache.get(cache_key)
if cached:
    return cached

result = expensive_calculation()
cache.set(cache_key, result, timeout=1800)
return result
```

### Pagination

Always paginate list endpoints:

```python
class MyView(generics.ListAPIView):
    pagination_class = StandardPagination
```

## Security Guidelines

### Input Validation

Always validate user input:

```python
class MySerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
```

### Authentication

Protect sensitive endpoints:

```python
class MyView(APIView):
    permission_classes = [IsAuthenticated]
```

### Environment Variables

Never commit sensitive data:

```python
# Good
API_KEY = config('TMDB_API_KEY')

# Bad
API_KEY = 'abc123xyz'  # Don't do this!
```

## Common Issues

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

### Database Issues

```bash
# Reset database
python manage.py flush
python manage.py migrate
```

### Redis Connection

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Start Redis if needed
redis-server
```

## Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows PEP 8 style guide
- [ ] All tests pass (`pytest`)
- [ ] New features have tests
- [ ] Code coverage maintained (>80%)
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts
- [ ] Changes are focused and related
- [ ] Environment variables documented
- [ ] No sensitive data committed

## Review Process

1. Automated checks run (tests, linting)
2. Code review by maintainers
3. Address feedback and make changes
4. Approval and merge

## Questions?

- Check existing issues and discussions
- Read the documentation at `/api/docs/`
- Ask questions in issues or discussions
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions help make this project better for everyone!

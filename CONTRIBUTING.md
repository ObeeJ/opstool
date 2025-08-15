# Contributing to OpsTool

We welcome contributions to OpsTool! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Go 1.21 or later
- Docker and Docker Compose
- Python 3.11 or later
- Node.js 18 or later
- PostgreSQL 15+
- Redis 7+

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/opstool.git
   cd opstool
   ```

3. Set up your development environment:
   ```bash
   # Install Go dependencies
   go mod download
   
   # Install Python dependencies
   cd scripts
   pip install -r requirements.txt
   cd ..
   
   # Install frontend dependencies
   cd frontend
   npm install
   cd ..
   
   # Start development services
   docker-compose up -d postgres redis jaeger
   ```

4. Run tests to ensure everything is working:
   ```bash
   go test ./...
   cd scripts && python -m pytest
   cd ../frontend && npm test
   ```

## Development Workflow

### Branching Strategy

- `master`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature development branches
- `hotfix/*`: Critical bug fixes

### Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation if needed

### Testing

#### Go Backend Tests
```bash
# Run all tests
go test ./...

# Run tests with coverage
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Run specific package tests
go test ./pkg/auth
```

#### Python Worker Tests
```bash
cd scripts
python -m pytest
python -m pytest tests/test_worker.py -v
```

#### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Code Quality

We use automated tools to maintain code quality:

- **Go**: `golangci-lint` for linting
- **Python**: `ruff` and `flake8` for linting, `black` for formatting
- **JavaScript/TypeScript**: `eslint` and `prettier`

Run before committing:
```bash
# Go
golangci-lint run

# Python
cd scripts
ruff check .
flake8 .

# Frontend
cd frontend
npm run lint
```

## Coding Standards

### Go Guidelines

- Follow [Effective Go](https://golang.org/doc/effective_go.html)
- Use `gofmt` for code formatting
- Write meaningful package and function documentation
- Use descriptive variable names
- Keep functions small and focused
- Handle errors explicitly

Example:
```go
// ValidateJWT validates a JWT token and returns claims
func ValidateJWT(tokenString string) (*Claims, error) {
    if tokenString == "" {
        return nil, errors.New("token is required")
    }
    
    // Implementation...
}
```

### Python Guidelines

- Follow [PEP 8](https://pep8.org/)
- Use type hints where applicable
- Write docstrings for all public functions
- Use descriptive variable names
- Keep functions under 50 lines when possible

Example:
```python
def process_alert(alert_data: Dict[str, Any]) -> AlertResult:
    """Process an incoming alert and determine appropriate action.
    
    Args:
        alert_data: Dictionary containing alert information
        
    Returns:
        AlertResult object with processing outcome
        
    Raises:
        ValidationError: If alert_data is invalid
    """
    # Implementation...
```

### Frontend Guidelines

- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Write unit tests for components
- Use descriptive component and prop names

## Commit Messages

Use conventional commits format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add JWT token refresh functionality

fix(database): resolve connection pool exhaustion

docs(api): update authentication endpoint documentation

test(health): add health check endpoint tests
```

## Pull Request Process

1. Ensure your branch is up to date with `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/your-feature
   git rebase develop
   ```

2. Push your branch and create a pull request
3. Fill out the pull request template
4. Ensure all CI checks pass
5. Request review from maintainers
6. Address review feedback
7. Once approved, a maintainer will merge your PR

### Pull Request Requirements

- [ ] All tests pass
- [ ] Code coverage is maintained or improved
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts
- [ ] Security considerations addressed

## Architecture Guidelines

### Backend (Go)

- Use dependency injection for better testability
- Follow clean architecture principles
- Separate business logic from HTTP handlers
- Use interfaces for external dependencies
- Implement proper error handling and logging

### Workers (Python)

- Use async/await for I/O operations
- Implement proper error handling and retries
- Use structured logging
- Follow the worker pattern for background tasks
- Implement health checks

### Frontend (Next.js)

- Use server-side rendering where appropriate
- Implement proper error boundaries
- Use React Query for data fetching
- Follow accessibility guidelines
- Implement responsive design

## Security Guidelines

- Never commit secrets or sensitive information
- Use environment variables for configuration
- Implement proper authentication and authorization
- Validate all inputs
- Use HTTPS in production
- Follow OWASP security guidelines
- Regular dependency updates

## Documentation

### Code Documentation

- Document all public APIs
- Include examples in documentation
- Keep documentation up to date with code changes
- Use clear and concise language

### Architecture Documentation

- Update architecture diagrams when needed
- Document design decisions
- Explain complex algorithms or business logic
- Maintain deployment documentation

## Getting Help

- Join our discussions on GitHub
- Check existing issues and documentation
- Ask questions in pull request reviews
- Reach out to maintainers for guidance

## Recognition

Contributors are recognized in our README and release notes. We appreciate all contributions, from code to documentation to bug reports!

Thank you for contributing to OpsTool! 🚀

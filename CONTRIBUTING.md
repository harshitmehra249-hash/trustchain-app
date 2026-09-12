# Contributing to TrustChain

Thank you for your interest in contributing to TrustChain! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Git Workflow](#git-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/trustchain-app.git`
3. Add upstream remote: `git remote add upstream https://github.com/harshitmehra249-hash/trustchain-app.git`
4. Create a feature branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Git

### Setup Steps

```bash
# Install dependencies
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install

# Start services
cd ..
docker-compose up -d
```

## Git Workflow

### Branch Naming Convention
- `feature/xxx` - New features
- `bugfix/xxx` - Bug fixes
- `hotfix/xxx` - Critical production fixes
- `docs/xxx` - Documentation updates
- `chore/xxx` - Maintenance, dependencies, etc.
- `test/xxx` - Test improvements

### Commit Messages

Use Conventional Commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring without feature changes
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance, dependency updates, etc.
- `ci`: CI/CD configuration changes

**Examples:**
```
feat(auth): Add OAuth2 Google integration

Implement OAuth2 flow for Google login with proper error handling

Closes #123

fix(mesh): Handle websocket disconnection gracefully
refactor(api): Extract validation logic to separate module
docs(contributing): Update contribution guidelines
```

## Coding Standards

### TypeScript (Frontend)

```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true
  }
}
```

**Rules:**
- Use strict mode in TypeScript
- Avoid `any` type; use proper typing
- All functions must have return type annotations
- Use React hooks, avoid class components
- Keep components small and focused
- Use meaningful variable/function names

### Python (Backend)

**Tools:**
- Linting: `ruff` (configured in `pyproject.toml`)
- Formatting: `black`
- Type checking: `mypy` (strict mode)

**Rules:**
- All functions must have type hints
- Docstrings for all public functions (Google style)
- Max line length: 100 characters
- Use async/await for I/O operations
- Handle exceptions explicitly, no bare `except`

**Example:**
```python
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user_by_email(
    email: str,
    db: AsyncSession
) -> Optional[User]:
    """
    Retrieve a user by email address.
    
    Args:
        email: User's email address
        db: Database session
        
    Returns:
        User object if found, None otherwise
        
    Raises:
        DatabaseError: If database query fails
    """
    try:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"Failed to fetch user: {e}")
        raise DatabaseError("Failed to fetch user") from e
```

### Solidity (Smart Contracts)

**Rules:**
- Use Solidity 0.8.20+
- Include SPDX license identifier
- Use OpenZeppelin libraries for standard contracts
- Gas optimize where possible
- Add comprehensive comments
- Use events for logging instead of storage

## Testing

### Frontend Tests (Vitest)
```bash
cd frontend
npm run test
npm run test:coverage
```

### Backend Tests (pytest)
```bash
cd backend
pytest tests/ --cov=app --cov-report=html
```

### Coverage Requirements
- Minimum 80% code coverage
- All new features must include tests
- Critical paths must have E2E tests

## Pull Request Process

1. **Before submitting:**
   - Pull latest changes from upstream
   - Run tests locally and ensure they pass
   - Run linters and fix any issues
   - Update documentation if needed
   - Sign off on commits (use `git commit -s`)

2. **Submission:**
   - Create PR against `develop` branch
   - Use descriptive title and description
   - Link related issues (use `Closes #123`)
   - Add relevant labels

3. **PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
Describe how to test changes

## Screenshots (if applicable)

## Checklist
- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings generated
```

4. **Review Process:**
   - At least 1 approval required
   - All CI checks must pass
   - Address review comments
   - Maintainers will merge when ready

## Issue Reporting

### Bug Report Template
```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior

## Actual Behavior

## Environment
- OS:
- Node.js/Python version:
- Browser (if applicable):

## Screenshots/Logs
```

### Feature Request Template
```markdown
## Description
Clear description of desired feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should it work?

## Alternatives Considered
```

## Questions?

Feel free to:
- Open an issue for questions
- Join our discussions
- Email: support@trustchain-app.dev

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to TrustChain! 🙏**

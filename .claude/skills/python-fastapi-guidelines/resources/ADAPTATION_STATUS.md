# Resource Files Adaptation Status

This directory contains resource files adapted from Node.js/Express/TypeScript patterns to Python/FastAPI patterns.

## Adaptation Progress

### ✅ Fully Adapted

None yet - resources need Python/FastAPI adaptation

### 🔄 Needs Adaptation

The following files currently contain Node.js/TypeScript examples and need Python/FastAPI equivalents:

1. **architecture-overview.md**
   - Update diagrams for FastAPI
   - Replace TypeScript examples with Python
   - Update service references (blog-api → gam-api)

2. **routing-and-controllers.md** → **routing-and-path-operations.md**
   - Rename to reflect FastAPI terminology
   - Replace Express Router with FastAPI APIRouter
   - Replace BaseController with FastAPI patterns
   - Update examples to use @router decorators

3. **validation-patterns.md** → **pydantic-models.md**
   - Rename to reflect Pydantic usage
   - Replace Zod schemas with Pydantic models
   - Show Field validators and model_validator
   - Update examples for BaseModel patterns

4. **async-and-errors.md**
   - Update async/await patterns for Python
   - Replace Node.js error patterns with Python exceptions
   - Show FastAPI HTTPException usage
   - Update error handling patterns

5. **middleware-guide.md**
   - Replace Express middleware with FastAPI middleware
   - Show Depends() for authentication
   - Update CORS configuration for FastAPI
   - Add async middleware examples

6. **configuration.md**
   - Replace unifiedConfig with Pydantic BaseSettings
   - Show environment variable loading
   - Update config patterns for Python
   - Add .env file examples

7. **database-patterns.md** → **api-client-patterns.md** (or remove)
   - Replace Prisma with API client patterns
   - Show async HTTP client usage (httpx)
   - Update for GAM API integration patterns
   - Or remove if not applicable

8. **services-and-repositories.md** → **business-logic-patterns.md**
   - Update to Python module organization
   - Remove repository pattern (not needed for API integration)
   - Focus on service functions and classes
   - Update dependency injection examples

9. **sentry-and-monitoring.md**
   - Update for Python Sentry SDK
   - Show sentry_sdk initialization
   - Update error capture patterns
   - Add FastAPI integration examples

10. **testing-guide.md**
    - Replace Jest with pytest
    - Show httpx AsyncClient usage
    - Update test patterns for Python
    - Add pytest fixtures examples

11. **complete-examples.md**
    - Replace all TypeScript examples with Python
    - Show complete FastAPI endpoint implementations
    - Use actual GAM API project patterns
    - Include Pydantic models, routing, error handling

### 📝 New Files Needed

1. **pydantic-models.md** - Comprehensive Pydantic guide
2. **routing-and-path-operations.md** - FastAPI routing guide
3. **dependency-injection.md** - FastAPI Depends system
4. **authentication-patterns.md** - API key, OAuth2, JWT for FastAPI
5. **performance-optimization.md** - Async optimization, caching

## Adaptation Guidelines

When adapting resources, follow these principles:

### Framework Mappings

| Node.js/Express | Python/FastAPI |
|-----------------|----------------|
| Express Router | FastAPI APIRouter |
| req, res | request model, return value |
| middleware | Depends() or middleware |
| Zod | Pydantic |
| Prisma | httpx / async clients |
| process.env | Pydantic BaseSettings |
| BaseController | function patterns or classes |
| try-catch | try-except |
| TypeScript types | Python type hints |

### Code Example Pattern

Always show:
1. ❌ Bad pattern (anti-pattern)
2. ✅ Good pattern (best practice)
3. Real project example from gam-api

### Project-Specific Updates

- Replace references to: blog-api, auth-service → gam-api, mcp-server
- Use actual project structure: packages/core, applications/api-server
- Reference real files: applications/api-server/routes/reports.py
- Use real models: GAMClient, ReportRequest, DateRange

## Priority Adaptation Order

1. **routing-and-path-operations.md** - Most commonly referenced
2. **pydantic-models.md** - Core validation pattern
3. **async-and-errors.md** - Critical for async FastAPI
4. **complete-examples.md** - Comprehensive reference
5. **testing-guide.md** - Essential for development
6. Remaining files as needed

## How to Adapt a Resource File

1. Read the original Node.js/Express version
2. Extract core architectural concepts (these are framework-agnostic)
3. Replace all code examples with Python/FastAPI equivalents
4. Update file references to match gam-api structure
5. Test examples against actual project code
6. Update this status file when complete

---

**Note**: The SKILL.md has been fully adapted. Resource files are next priority.
**Created**: 2025-10-30
**Project**: gam-api (Python/FastAPI Google Ad Manager API)

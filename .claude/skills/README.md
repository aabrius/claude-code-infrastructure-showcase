# Skills

Production-tested skills for Claude Code that auto-activate based on context.
**Project:** Google Ad Manager API (Python/FastAPI)

---

## What Are Skills?

Skills are modular knowledge bases that Claude loads when needed. They provide:
- Domain-specific guidelines
- Best practices
- Code examples
- Anti-patterns to avoid

**Problem:** Skills don't activate automatically by default.

**Solution:** This project includes hooks + configuration to make them activate.

---

## Available Skills

### skill-developer (Meta-Skill)
**Purpose:** Creating and managing Claude Code skills

**Files:** 7 resource files (426 lines total)

**Use when:**
- Creating new skills
- Understanding skill structure
- Working with skill-rules.json
- Debugging skill activation

**Customization:** ✅ None - tech-agnostic

**[View Skill →](skill-developer/)**

---

### python-fastapi-guidelines
**Purpose:** Python/FastAPI development patterns with Pydantic validation

**Files:** Main SKILL.md + 11 resource files (adapted for Python/FastAPI)

**Tech Stack:** Python 3.8+, FastAPI, Pydantic, async/await

**Covers:**
- Clean architecture (Routes → Business Logic → Data Access)
- FastAPI routing and path operations
- Pydantic models for validation
- Async/await patterns and error handling
- Dependency injection with FastAPI Depends
- API authentication (API key, OAuth2, JWT)
- Middleware (CORS, logging, auth)
- Structured logging and error tracking
- Testing with pytest and httpx

**Use when:**
- Creating/modifying API routes
- Building FastAPI routers
- Implementing Pydantic models
- Setting up async endpoints
- Adding authentication
- Error handling patterns

**Customization:** ✅ Already customized for gam-api project

**Current pathPatterns:**
```json
{
  "pathPatterns": [
    "packages/core/src/gam_api/**/*.py",
    "packages/shared/src/gam_shared/**/*.py",
    "packages/sdk/src/gam_sdk/**/*.py",
    "applications/api-server/**/*.py",
    "applications/mcp-server/**/*.py",
    "scripts/**/*.py",
    "**/routes/**/*.py",
    "**/adapters/**/*.py",
    "**/builders/**/*.py"
  ]
}
```

**Adaptation Status:**
- ✅ Main SKILL.md fully adapted
- ✅ routing-and-path-operations.md created (Python/FastAPI)
- ⚠️ 10 resource files contain original Node.js examples (see resources/ADAPTATION_STATUS.md)
- 📝 Architectural concepts remain valid, code examples need Python translation

**[View Skill →](python-fastapi-guidelines/)**

---

### route-tester
**Purpose:** Testing authenticated API routes

**Files:** 1 main file (389 lines)

**Covers:**
- API testing with authentication
- Testing POST/PUT/DELETE operations
- Debugging auth issues
- Validating route functionality

**Customization:** ✅ Adapted for FastAPI + API key authentication

**Original:** JWT cookie-based auth (Node.js/Express)
**Adapted for:** API key authentication (Python/FastAPI)

**Use when:**
- Testing API endpoints
- Debugging authentication
- Validating route responses

**[View Skill →](route-tester/)**

---

### error-tracking
**Purpose:** Sentry error tracking and monitoring patterns

**Files:** 1 main file (~250 lines)

**Covers:**
- Sentry initialization (Python SDK)
- Error capture patterns
- Breadcrumbs and user context
- Performance monitoring
- Integration with FastAPI

**Use when:**
- Setting up error tracking
- Capturing exceptions
- Adding error context
- Debugging production issues

**Customization:** ✅ Updated for Python patterns

**Current pathPatterns:**
```json
{
  "pathPatterns": [
    "**/sentry*.py",
    "**/*_service.py",
    "**/routes/**/*.py",
    "applications/**/*.py"
  ]
}
```

**[View Skill →](error-tracking/)**

---

### brainstorming
**Purpose:** Refine rough ideas through structured Socratic questioning

**Files:** 1 main file

**Use when:**
- Planning new features
- Designing system architecture
- Exploring alternative approaches
- Before implementation

**Customization:** ✅ None - tech-agnostic

**[View Skill →](brainstorming/)**

---

## Project Structure Context

This is a Python monorepo with the following structure:

```
gam-api/
├── packages/                    # Reusable components
│   ├── core/                   # GAM API functionality
│   ├── sdk/                    # Python SDK
│   └── shared/                 # Utilities
├── applications/               # Deployable services
│   ├── api-server/            # FastAPI REST API
│   └── mcp-server/            # FastMCP server
├── scripts/                    # Utility scripts
└── tests/                      # Test suites
```

**Skills are configured to trigger on:**
- Python files in packages/ and applications/
- Files containing FastAPI decorators (`@router.get`, `@app.post`)
- Files with Pydantic models (`class Model(BaseModel)`)
- Files with async patterns (`async def`)

---

## How Skills Auto-Activate

### By File Path
When you edit files matching `pathPatterns`:
```python
# Editing this file triggers python-fastapi-guidelines:
applications/api-server/routes/reports.py
```

### By Keywords in Prompts
When you use trigger keywords:
```
"create a new FastAPI route"        → python-fastapi-guidelines
"add pydantic validation"           → python-fastapi-guidelines
"test API endpoint"                 → route-tester
"add error tracking"                → error-tracking
```

### By File Content
When files contain trigger patterns:
```python
from fastapi import APIRouter       # → python-fastapi-guidelines
class MyRequest(BaseModel):         # → python-fastapi-guidelines
async def my_function():            # → python-fastapi-guidelines
```

---

## skill-rules.json Configuration

### What It Does

Defines when skills should activate based on:
- **Keywords** in user prompts ("fastapi", "pydantic", "async")
- **Intent patterns** (regex matching user intent)
- **File path patterns** (editing Python backend files)
- **Content patterns** (code contains FastAPI imports)

### Configuration Format

```json
{
  "skill-name": {
    "type": "domain" | "guardrail",
    "enforcement": "suggest" | "block",
    "priority": "high" | "medium" | "low",
    "promptTriggers": {
      "keywords": ["list", "of", "keywords"],
      "intentPatterns": ["regex patterns"]
    },
    "fileTriggers": {
      "pathPatterns": ["path/to/files/**/*.py"],
      "contentPatterns": ["from fastapi import"]
    }
  }
}
```

### Enforcement Levels

- **suggest**: Skill appears as suggestion, doesn't block
- **block**: Must use skill before proceeding (guardrail)

**Current project uses "suggest" for all skills** - recommendations without blocking.

---

## Adaptation Notes

This project started from a Node.js/Express/TypeScript skill showcase and was adapted for Python/FastAPI:

### What Was Changed
✅ Renamed `backend-dev-guidelines` → `python-fastapi-guidelines`
✅ Updated all path patterns to match Python monorepo structure
✅ Updated keywords: Express → FastAPI, Zod → Pydantic, TypeScript → Python
✅ Updated content patterns: `.ts` → `.py`, `router.` → `@router.`
✅ Removed `frontend-dev-guidelines` (no React frontend)
✅ Adapted `route-tester` for API key auth (was JWT cookie)
✅ Adapted `error-tracking` for Python Sentry SDK

### Main Skill (SKILL.md)
✅ **Fully adapted** - All examples use Python/FastAPI/Pydantic patterns

### Resource Files
⚠️ **Partially adapted** - See `python-fastapi-guidelines/resources/ADAPTATION_STATUS.md`
- ✅ routing-and-path-operations.md - Fully Python/FastAPI
- ⚠️ 10 files still contain Node.js/TypeScript examples
- 📝 Architectural concepts remain valid (layered architecture, separation of concerns)
- 🔄 Code examples need Python translation as used

**Priority for adaptation:**
1. pydantic-models.md
2. async-and-errors.md
3. complete-examples.md
4. testing-guide.md

---

## Creating Your Own Skills

See the **skill-developer** skill for complete guide on:
- Skill YAML frontmatter structure
- Resource file organization
- Trigger pattern design
- Testing skill activation

**Quick template:**
```markdown
---
name: my-skill
description: What this skill does
---

# My Skill Title

## Purpose
[Why this skill exists]

## When to Use This Skill
[Auto-activation scenarios]

## Quick Reference
[Key patterns and examples]

## Resource Files
- [topic-1.md](resources/topic-1.md)
- [topic-2.md](resources/topic-2.md)
```

---

## Troubleshooting

### Skill isn't activating

**Check:**
1. Is skill directory in `.claude/skills/`?
2. Is skill listed in `skill-rules.json`?
3. Do `pathPatterns` match your files?
4. Are hooks installed and working?
5. Is settings.json configured correctly?

**Debug:**
```bash
# Check skill exists
ls -la .claude/skills/

# Validate skill-rules.json
jq empty .claude/skills/skill-rules.json && echo "✅ Valid JSON"

# Check hooks are executable
ls -la .claude/hooks/*.sh

# Test hook manually
./.claude/hooks/skill-activation-prompt.sh
```

### Skill activates too often

Update skill-rules.json:
- Make keywords more specific
- Narrow `pathPatterns`
- Increase specificity of `intentPatterns`

### Skill never activates

Update skill-rules.json:
- Add more keywords
- Broaden `pathPatterns`
- Add more `intentPatterns`

### Verifying Activation

Test by editing a matching file:
```bash
# This should trigger python-fastapi-guidelines:
code applications/api-server/routes/reports.py

# Or use a keyword in prompt:
# "Create a new FastAPI endpoint for user management"
```

---

## Project-Specific Configuration

### GAM API Project

**Tech Stack:**
- Python 3.8+
- FastAPI for REST API
- Pydantic for validation
- OAuth2 + API key authentication
- Google Ad Manager API integration
- FastMCP for MCP server

**Key Directories:**
- `packages/core/` - Core GAM API functionality
- `packages/shared/` - Shared utilities
- `applications/api-server/` - FastAPI REST service
- `applications/mcp-server/` - FastMCP server

**Skill Activation Scope:**
All Python files in packages/ and applications/ directories will trigger `python-fastapi-guidelines` when edited.

---

## Next Steps

1. ✅ **Skills configured** - python-fastapi-guidelines, route-tester, error-tracking, skill-developer, brainstorming
2. ✅ **Paths customized** - All pathPatterns match your Python monorepo structure
3. ✅ **Hooks active** - skill-activation-prompt and post-tool-use-tracker enabled
4. 📝 **Test activation** - Edit a Python file and observe skill suggestion
5. 🔄 **Adapt resources** - Translate remaining Node.js examples to Python as needed

**Skills are production-ready and will auto-activate based on your Python/FastAPI development context.**

---

**Project**: gam-api - Google Ad Manager API Integration
**Stack**: Python 3.8+, FastAPI, Pydantic, OAuth2
**Architecture**: Monorepo with packages and applications
**Last Updated**: 2025-10-30

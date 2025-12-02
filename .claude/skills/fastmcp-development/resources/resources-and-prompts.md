# FastMCP Resources and Prompts

## Table of Contents

1. [Resources Overview](#resources-overview)
2. [Static Resources](#static-resources)
3. [Dynamic Resources](#dynamic-resources)
4. [URI Templates](#uri-templates)
5. [Prompts](#prompts)
6. [Best Practices](#best-practices)

---

## Resources Overview

Resources provide **read-only data access** for MCP clients. They load information into an LLM's context, similar to GET endpoints.

### Resource Types

| Type | Description | Use Case |
|------|-------------|----------|
| Static | Pre-defined, constant data | Config files, schemas |
| Dynamic | Generated on request | User data, API responses |
| Template | URI pattern matching | Parameterized queries |

---

## Static Resources

### TextResource

```python
from fastmcp import FastMCP
from fastmcp.resources import TextResource

mcp = FastMCP("MyServer")

# Add static text resource
mcp.add_resource(TextResource(
    uri="config://app/settings",
    name="App Settings",
    description="Application configuration",
    content="""
    {
        "version": "1.0.0",
        "environment": "production",
        "features": ["auth", "reports"]
    }
    """
))
```

### FileResource

```python
from fastmcp.resources import FileResource

# Serve a file as resource
mcp.add_resource(FileResource(
    uri="file://schema/report.json",
    path="/app/schemas/report.json",
    name="Report Schema",
    description="JSON schema for report validation"
))
```

### DirectoryResource

```python
from fastmcp.resources import DirectoryResource

# Serve all files in a directory
mcp.add_resource(DirectoryResource(
    uri="docs://api",
    path="/app/docs/api",
    name="API Documentation",
    description="API documentation files"
))
```

---

## Dynamic Resources

### Basic Dynamic Resource

```python
@mcp.resource("status://server")
def get_server_status() -> dict:
    """Current server status."""
    return {
        "status": "healthy",
        "uptime": get_uptime_seconds(),
        "memory_usage": get_memory_usage(),
        "active_connections": get_connection_count()
    }
```

### Async Dynamic Resource

```python
@mcp.resource("data://latest")
async def get_latest_data() -> dict:
    """Fetch latest data from external API."""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()
```

### Resource with Error Handling

```python
from fastmcp.exceptions import ResourceError

@mcp.resource("user://profile")
async def get_user_profile() -> dict:
    """Get current user profile."""
    try:
        profile = await fetch_profile()
        if not profile:
            raise ResourceError("Profile not found")
        return profile
    except APIError as e:
        raise ResourceError(f"Failed to fetch profile: {e}")
```

---

## URI Templates

URI templates follow RFC 6570 for parameterized resources.

### Simple Parameters

```python
# {param} matches single path segment
@mcp.resource("users://{user_id}/profile")
async def get_user_profile(user_id: str) -> dict:
    """Get user profile by ID."""
    return await fetch_user(user_id)

# Multiple parameters
@mcp.resource("repos://{owner}/{repo}/info")
async def get_repo_info(owner: str, repo: str) -> dict:
    """Get repository information."""
    return await fetch_repo(owner, repo)
```

**Usage:**
- `users://123/profile` → `user_id="123"`
- `repos://jlowin/fastmcp/info` → `owner="jlowin"`, `repo="fastmcp"`

### Wildcard Parameters

```python
# {param*} captures multiple segments including slashes
@mcp.resource("files://{path*}")
async def get_file_content(path: str) -> str:
    """Read file at path."""
    return read_file(f"/{path}")
```

**Usage:**
- `files://docs/api/README.md` → `path="docs/api/README.md"`

### Query Parameters

```python
# {?param1,param2} for optional configuration
@mcp.resource("search://{query}{?limit,offset}")
async def search_items(
    query: str,
    limit: int = 10,
    offset: int = 0
) -> List[dict]:
    """Search items with pagination."""
    return await search(query, limit=limit, offset=offset)
```

**Usage:**
- `search://python` → `query="python"`, defaults
- `search://python?limit=20&offset=10` → with pagination

### Type Coercion

Query parameters automatically convert to annotated types:

```python
@mcp.resource("items://{category}{?min_price,max_price,in_stock}")
async def get_items(
    category: str,
    min_price: float = 0.0,
    max_price: float = 1000.0,
    in_stock: bool = True
) -> List[dict]:
    """Get items with filters."""
    return await fetch_items(category, min_price, max_price, in_stock)
```

**Usage:**
- `items://electronics?min_price=100&in_stock=true`
- Parameters coerced: `min_price=100.0`, `in_stock=True`

---

## Prompts

Prompts are reusable, parameterized templates for LLM interactions.

### Basic Prompt

```python
@mcp.prompt
def code_review(code: str, language: str = "python") -> str:
    """Generate a code review prompt."""
    return f"""Please review the following {language} code:

```{language}
{code}
```

Focus on:
1. Code quality and readability
2. Potential bugs or issues
3. Performance considerations
4. Best practices
"""
```

### Multi-Message Prompt

```python
from fastmcp.prompts import Message

@mcp.prompt
def conversation_starter(topic: str) -> List[Message]:
    """Start a conversation about a topic."""
    return [
        Message(role="system", content=f"You are an expert on {topic}."),
        Message(role="user", content=f"Tell me about {topic}.")
    ]
```

### Prompt with Context

```python
@mcp.prompt
def analysis_prompt(
    data: str,
    analysis_type: Literal["summary", "detailed", "comparative"]
) -> str:
    """Generate data analysis prompt."""
    instructions = {
        "summary": "Provide a brief summary of the key points.",
        "detailed": "Provide a comprehensive analysis with all details.",
        "comparative": "Compare and contrast the different elements."
    }

    return f"""Analyze the following data:

{data}

{instructions[analysis_type]}

Structure your response with clear headings and bullet points.
"""
```

### Dynamic Prompt Content

```python
@mcp.prompt
async def report_prompt(report_type: str) -> str:
    """Generate report creation prompt with dynamic template."""
    # Load template from resource or file
    template = await load_template(report_type)

    return f"""Create a {report_type} report using this template:

{template}

Fill in all sections with relevant information.
"""
```

---

## Best Practices

### Resource Design

1. **Use clear URI schemes**
   ```python
   # Good: descriptive schemes
   "users://{id}/profile"
   "reports://{type}/{date}"
   "config://app/settings"

   # Avoid: ambiguous schemes
   "data://{id}"
   "get://{thing}"
   ```

2. **Return consistent formats**
   ```python
   @mcp.resource("items://{id}")
   async def get_item(id: str) -> dict:
       """Always return same structure."""
       return {
           "id": id,
           "data": await fetch_item(id),
           "metadata": {
               "fetched_at": datetime.now().isoformat()
           }
       }
   ```

3. **Handle missing resources gracefully**
   ```python
   @mcp.resource("users://{id}")
   async def get_user(id: str) -> dict:
       user = await fetch_user(id)
       if not user:
           raise ResourceError(f"User {id} not found")
       return user
   ```

### Prompt Design

1. **Be specific about format expectations**
   ```python
   @mcp.prompt
   def structured_output(data: str) -> str:
       return f"""Analyze this data and respond in JSON format:

   {data}

   Response format:
   {{
       "summary": "...",
       "key_points": ["...", "..."],
       "recommendations": ["...", "..."]
   }}
   """
   ```

2. **Include examples when helpful**
   ```python
   @mcp.prompt
   def classification_prompt(text: str) -> str:
       return f"""Classify the following text:

   Text: {text}

   Categories: positive, negative, neutral

   Examples:
   - "Great product!" → positive
   - "Terrible experience" → negative
   - "It arrived on time" → neutral

   Respond with only the category name.
   """
   ```

3. **Use system messages for context**
   ```python
   @mcp.prompt
   def expert_prompt(domain: str, question: str) -> List[Message]:
       return [
           Message(
               role="system",
               content=f"You are an expert in {domain}. "
                       "Provide accurate, detailed responses."
           ),
           Message(role="user", content=question)
       ]
   ```

### Performance

1. **Cache expensive resources**
   ```python
   from functools import lru_cache
   from datetime import datetime, timedelta

   _cache = {}
   _cache_ttl = timedelta(minutes=5)

   @mcp.resource("expensive://data")
   async def get_expensive_data() -> dict:
       cache_key = "expensive_data"
       now = datetime.now()

       if cache_key in _cache:
           data, cached_at = _cache[cache_key]
           if now - cached_at < _cache_ttl:
               return {**data, "cached": True}

       data = await expensive_fetch()
       _cache[cache_key] = (data, now)
       return {**data, "cached": False}
   ```

2. **Use lazy loading for large resources**
   ```python
   @mcp.resource("large://{page}")
   async def get_large_data(page: int = 1) -> dict:
       """Paginated large data access."""
       page_size = 100
       offset = (page - 1) * page_size

       items = await fetch_items(limit=page_size, offset=offset)
       total = await get_total_count()

       return {
           "items": items,
           "page": page,
           "total_pages": (total + page_size - 1) // page_size,
           "total_items": total
       }
   ```

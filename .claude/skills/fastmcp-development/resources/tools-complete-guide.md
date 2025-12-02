# FastMCP Tools Complete Guide

## Table of Contents

1. [Tool Basics](#tool-basics)
2. [Decorator Configuration](#decorator-configuration)
3. [Parameter Types & Validation](#parameter-types--validation)
4. [Parameter Metadata](#parameter-metadata)
5. [Return Values & Structured Output](#return-values--structured-output)
6. [ToolResult for Full Control](#toolresult-for-full-control)
7. [Output Schemas](#output-schemas)
8. [Error Handling](#error-handling)
9. [Context Injection](#context-injection)
10. [Annotations](#annotations)
11. [Tool Management](#tool-management)
12. [Async Patterns](#async-patterns)
13. [Best Practices](#best-practices)

---

## Tool Basics

Tools are Python functions decorated with `@mcp.tool` that expose capabilities to LLMs. FastMCP automatically converts function signatures into MCP schemas.

### Minimal Tool

```python
from fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool
async def hello(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"
```

**What FastMCP does automatically:**
- Uses function name as tool identifier
- Extracts docstring for description
- Generates JSON schema from type annotations
- Validates parameters and serializes results

---

## Decorator Configuration

The `@mcp.tool` decorator accepts comprehensive parameters:

```python
@mcp.tool(
    name="custom_tool_name",           # Override function name
    description="Custom description",   # Override docstring
    tags={"reporting", "data"},         # Categorization tags
    enabled=True,                       # Enable/disable (default: True)
    icons=[Icon(type="emoji", icon="🔧")],  # Visual icons (v2.14.0+)
    exclude_args=["internal_param"],    # Hide args from LLM schema
    annotations={                       # MCP behavioral metadata
        "title": "Friendly Name",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    meta={"version": "1.0"},           # Custom metadata (v2.11.0+)
    output_schema={...}                # Custom JSON Schema for returns
)
async def my_tool(): pass
```

### Parameter Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | function name | Tool identifier |
| `description` | str | docstring | Tool explanation |
| `tags` | set[str] | None | Categorization strings |
| `enabled` | bool | True | Activate/deactivate |
| `icons` | list[Icon] | None | Visual representations |
| `exclude_args` | list[str] | None | Hide from schema |
| `annotations` | dict/ToolAnnotations | None | MCP metadata |
| `meta` | dict | None | Custom metadata |
| `output_schema` | dict | None | Return JSON Schema |

---

## Parameter Types & Validation

### Supported Types

FastMCP supports comprehensive type annotations:

```python
from typing import List, Dict, Optional, Union, Literal, Set
from datetime import datetime
from pathlib import Path
from uuid import UUID
from enum import Enum
from pydantic import BaseModel
from dataclasses import dataclass

# Basic types
def tool1(text: str, count: int, ratio: float, active: bool): pass

# Collections
def tool2(items: List[str], mapping: Dict[str, int], unique: Set[str]): pass

# Optional and Union
def tool3(name: Optional[str] = None, value: Union[int, str] = 0): pass

# Constrained types
class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

def tool4(
    format: Literal["json", "csv", "xml"],
    color: Color
): pass

# Specialized types
def tool5(
    timestamp: datetime,
    file_path: Path,
    identifier: UUID,
    binary_data: bytes
): pass

# Pydantic models
class Config(BaseModel):
    name: str
    value: int
    tags: List[str] = []

def tool6(config: Config): pass

# Dataclasses
@dataclass
class Item:
    id: str
    quantity: int

def tool7(item: Item): pass
```

### Validation Modes

```python
# Flexible validation (default): Coerces compatible types
# "10" → 10, "true" → True
mcp = FastMCP("FlexibleServer")

# Strict validation: Rejects type mismatches
# "10" → ValidationError
mcp = FastMCP("StrictServer", strict_input_validation=True)
```

### Required vs Optional Parameters

```python
@mcp.tool
async def search(
    query: str,                      # Required (no default)
    category: str | None = None,     # Optional (default: None)
    limit: int = 10,                 # Optional (default: 10)
    include_metadata: bool = False   # Optional (default: False)
) -> List[dict]:
    """Search with optional parameters."""
    pass
```

**Rule:** Parameters without defaults are required; parameters with defaults are optional.

---

## Parameter Metadata

### Simple Descriptions with Annotated

```python
from typing import Annotated

@mcp.tool
async def process(
    url: Annotated[str, "The URL to process"],
    timeout: Annotated[int, "Timeout in seconds"] = 30
) -> dict:
    """Process a URL with timeout."""
    pass
```

### Pydantic Field for Validation

```python
from pydantic import Field

@mcp.tool
async def create_report(
    name: Annotated[str, Field(
        min_length=1,
        max_length=100,
        description="Report name"
    )],
    days_back: Annotated[int, Field(
        ge=1,
        le=365,
        description="Days to look back"
    )] = 30,
    email: Annotated[str, Field(
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
        description="Email for notifications"
    )] = None
) -> dict:
    """Create a report with validated parameters."""
    pass
```

### Field Validation Options

| Validation | Description | Example |
|------------|-------------|---------|
| `ge` / `gt` | Greater than or equal / greater than | `Field(ge=0)` |
| `le` / `lt` | Less than or equal / less than | `Field(le=100)` |
| `min_length` | Minimum string length | `Field(min_length=1)` |
| `max_length` | Maximum string length | `Field(max_length=255)` |
| `pattern` | Regex pattern | `Field(pattern=r"^\d{4}$")` |
| `multiple_of` | Numeric multiple | `Field(multiple_of=5)` |

---

## Return Values & Structured Output

### Automatic Content Conversion

| Return Type | MCP Content |
|-------------|-------------|
| `str` | TextContent |
| `dict`, `list` | Structured JSON |
| `bytes` | Base64-encoded BlobResourceContents |
| `Pydantic model` | Serialized JSON |
| `Image` | ImageContent |
| `Audio` | AudioContent |
| `File` | EmbeddedResource |
| `None` | Empty response |

### Structured Output (v2.10.0+)

Object-like returns automatically generate structured content:

```python
@mcp.tool
async def get_stats() -> dict:
    """Returns structured JSON."""
    return {
        "total": 100,
        "active": 85,
        "rate": 0.85
    }
```

### Primitive Returns with Type Hints

Primitives with return type annotations are wrapped:

```python
@mcp.tool
async def calculate(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b  # Returns {"result": <value>}
```

### Media Content Helpers

```python
from fastmcp.utilities.types import Image, Audio, File

@mcp.tool
async def get_image(image_id: str) -> Image:
    """Return an image."""
    return Image(path="/path/to/image.png")
    # or: Image(data=bytes_data, format="png")

@mcp.tool
async def get_audio(audio_id: str) -> Audio:
    """Return audio file."""
    return Audio(path="/path/to/audio.mp3")

@mcp.tool
async def get_file(file_id: str) -> File:
    """Return any file."""
    return File(path="/path/to/document.pdf")
```

---

## ToolResult for Full Control

For explicit control over all output aspects:

```python
from fastmcp.tools.tool import ToolResult

@mcp.tool
async def advanced_operation() -> ToolResult:
    """Operation with full control over output."""
    return ToolResult(
        # Human-readable content (string, list, or serializable)
        content="Operation completed successfully",

        # Structured JSON data
        structured_content={
            "status": "success",
            "data": {"key": "value"},
            "metrics": {
                "processed": 100,
                "errors": 0
            }
        },

        # Runtime metadata (v2.13.1+)
        meta={
            "execution_time_ms": 145,
            "cache_hit": False,
            "version": "1.0"
        }
    )
```

### ToolResult Fields

| Field | Type | Description |
|-------|------|-------------|
| `content` | str/list/Any | Traditional MCP blocks |
| `structured_content` | dict | JSON matching output schema |
| `meta` | dict | Runtime execution metadata |

---

## Output Schemas

### Automatic Schema Generation

Return type annotations generate JSON schemas:

```python
from pydantic import BaseModel
from typing import List

class ReportResult(BaseModel):
    id: str
    status: str
    data: List[dict]
    total_rows: int

@mcp.tool
async def generate_report() -> ReportResult:
    """Generate a report with typed output."""
    return ReportResult(
        id="report_123",
        status="complete",
        data=[{"row": 1}],
        total_rows=1
    )
```

### Custom Output Schema

```python
@mcp.tool(
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {"type": "object"},
            "error": {"type": "string"}
        },
        "required": ["success"]
    }
)
async def custom_schema_tool() -> dict:
    """Tool with custom output schema."""
    return {"success": True, "data": {"key": "value"}}
```

---

## Error Handling

### ToolError for User-Facing Errors

```python
from fastmcp.exceptions import ToolError

@mcp.tool
async def safe_divide(a: float, b: float) -> float:
    """Divide two numbers safely."""
    if b == 0:
        raise ToolError("Cannot divide by zero. Please provide a non-zero divisor.")
    return a / b
```

### Masking Error Details

```python
# Hide implementation details from clients
mcp = FastMCP("SecureServer", mask_error_details=True)

@mcp.tool
async def protected_operation():
    # Internal errors show generic message
    raise ValueError("Internal error")  # Client sees: "An error occurred"

    # ToolError messages always shown
    raise ToolError("This message is visible")  # Client sees this
```

### Structured Error Responses

```python
import json
from typing import List, Optional

def format_error(
    error_type: str,
    message: str,
    code: Optional[str] = None,
    suggestions: Optional[List[str]] = None
) -> str:
    """Format consistent error response."""
    return json.dumps({
        "success": False,
        "error": {
            "type": error_type,
            "message": message,
            "code": code,
            "suggestions": suggestions or []
        }
    }, indent=2)

@mcp.tool
async def validated_action(param: str) -> str:
    """Action with structured error handling."""
    if not param.strip():
        return format_error(
            "ValidationError",
            "Parameter cannot be empty",
            "VAL_001",
            ["Provide a non-empty string value"]
        )

    try:
        result = await perform_action(param)
        return json.dumps({"success": True, "result": result})
    except APIError as e:
        return format_error(
            "APIError",
            str(e),
            "API_001",
            ["Check API credentials", "Verify network connectivity"]
        )
```

---

## Context Injection

### Basic Context Access

```python
from fastmcp import Context

@mcp.tool
async def context_tool(data: str, ctx: Context) -> dict:
    """Tool with MCP context access."""
    # Context parameter is optional and not exposed in schema
    await ctx.info(f"Processing: {data}")
    return {"processed": data}
```

### Context Methods Reference

```python
@mcp.tool
async def full_context_demo(param: str, ctx: Context) -> dict:
    """Demonstrate all context capabilities."""

    # === LOGGING ===
    await ctx.debug("Debug message")
    await ctx.info("Info message")
    await ctx.warning("Warning message")
    await ctx.error("Error message")

    # === PROGRESS REPORTING ===
    await ctx.report_progress(progress=25, total=100)
    await ctx.report_progress(progress=50, total=100)
    await ctx.report_progress(progress=100, total=100)

    # === RESOURCE ACCESS ===
    resources = await ctx.list_resources()
    content = await ctx.read_resource("config://settings")

    # === PROMPT ACCESS (v2.13.0+) ===
    prompts = await ctx.list_prompts()
    prompt_result = await ctx.get_prompt("analyze", {"data": param})

    # === LLM SAMPLING (v2.0.0+) ===
    response = await ctx.sample(
        "Summarize this data",
        temperature=0.7
    )

    # === USER ELICITATION (v2.10.0+) ===
    user_input = await ctx.elicit(
        "Enter your name:",
        response_type=str
    )

    # === STATE MANAGEMENT (v2.11.0+) ===
    ctx.set_state("processing_started", True)
    started = ctx.get_state("processing_started")

    # === REQUEST METADATA ===
    request_id = ctx.request_id
    client_id = ctx.client_id
    session_id = ctx.session_id  # HTTP only

    return {"status": "complete", "request_id": request_id}
```

### Context in Helper Functions

```python
from fastmcp.server.dependencies import get_context

async def helper_function():
    """Access context from nested functions."""
    ctx = get_context()
    await ctx.info("Helper function called")
```

---

## Annotations

Annotations provide behavioral metadata to clients:

```python
@mcp.tool(
    annotations={
        "title": "Calculate Sum",          # Display name
        "readOnlyHint": True,              # Only reads data
        "destructiveHint": False,          # No destructive changes
        "idempotentHint": True,            # Repeatable safely
        "openWorldHint": False             # No external systems
    }
)
async def calculate_sum(numbers: List[float]) -> float:
    """Sum a list of numbers."""
    return sum(numbers)
```

### Annotation Reference

| Annotation | Type | Description |
|------------|------|-------------|
| `title` | string | Human-friendly display name |
| `readOnlyHint` | bool | Tool only reads data |
| `destructiveHint` | bool | Makes destructive changes |
| `idempotentHint` | bool | Same result on repeat calls |
| `openWorldHint` | bool | Interacts with external systems |

---

## Tool Management

### Excluding Arguments

Hide internal parameters from LLM schema:

```python
@mcp.tool(exclude_args=["internal_id"])
async def process_item(
    item_name: str,
    internal_id: str = "default_id"  # Hidden from LLM
) -> dict:
    """Process an item."""
    return {"name": item_name, "id": internal_id}
```

### Dynamic Enable/Disable

```python
@mcp.tool(enabled=False)
async def maintenance_tool():
    """Tool disabled by default."""
    pass

# Enable at runtime
maintenance_tool.enable()

# Disable at runtime
maintenance_tool.disable()
```

### Removing Tools

```python
mcp.remove_tool("tool_name")
```

### Duplicate Handling

```python
mcp = FastMCP(
    name="Server",
    on_duplicate_tools="error"  # Options: "warn", "error", "replace", "ignore"
)
```

### Notifications (v2.9.1+)

Adding, removing, enabling, or disabling tools triggers `notifications/tools/list_changed` to connected clients.

---

## Async Patterns

### Prefer Async for I/O

```python
import httpx

@mcp.tool
async def fetch_data(url: str) -> dict:
    """Fetch data from URL (async)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### Wrap Blocking Operations

```python
import anyio

def cpu_intensive_task(data: str) -> str:
    """Blocking CPU-bound operation."""
    # Heavy computation
    return processed_data

@mcp.tool
async def process_heavy(data: str) -> str:
    """Wrap blocking code for async context."""
    result = await anyio.to_thread.run_sync(cpu_intensive_task, data)
    return result
```

### Concurrent Operations

```python
import asyncio

@mcp.tool
async def batch_fetch(urls: List[str]) -> List[dict]:
    """Fetch multiple URLs concurrently."""
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
```

---

## Best Practices

### Do

1. **Always use type annotations** - Required for schema generation
2. **Write clear docstrings** - Shown to LLMs for tool selection
3. **Use async for I/O** - Prevents blocking the event loop
4. **Validate with Pydantic Field** - Use constraints for better validation
5. **Return structured data** - Easier for clients to process
6. **Use ToolError** - For user-facing error messages
7. **Report progress** - For long-running operations
8. **Log with context** - Use `ctx.info()`, `ctx.error()` etc.
9. **Use annotations** - Help clients understand tool behavior

### Don't

1. **Skip type annotations** - Schema generation fails
2. **Use `*args`/`**kwargs`** - Not supported
3. **Block event loop** - Use async or `anyio.to_thread`
4. **Hardcode secrets** - Use environment variables
5. **Return raw exceptions** - Leak implementation details
6. **Ignore errors** - Always handle and report
7. **Skip docstrings** - Poor tool discovery
8. **Return large data** - Consider pagination

### Code Quality Checklist

- [ ] Type annotations on all parameters and return
- [ ] Clear docstring describing purpose
- [ ] Async function for I/O operations
- [ ] Proper error handling with ToolError
- [ ] Progress reporting for long operations
- [ ] Validation using Pydantic Field
- [ ] Meaningful parameter descriptions
- [ ] Appropriate annotations set

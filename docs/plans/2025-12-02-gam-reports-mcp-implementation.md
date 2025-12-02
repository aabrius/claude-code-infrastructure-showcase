# GAM Reports MCP Server Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a standalone MCP server for GAM report management with 7 goal-oriented tools and a Pydantic knowledge base.

**Architecture:** FastMCP server with layered structure - models (knowledge base), endpoints (one per GAM REST endpoint), core (auth + client), and server.py (MCP tools). Uses aiohttp for async HTTP.

**Tech Stack:** Python 3.11+, FastMCP 2.x, aiohttp, Pydantic 2.x, pydantic-settings, google-auth

---

## Task 1: Project Scaffolding

**Files:**
- Create: `applications/gam-reports-mcp/pyproject.toml`
- Create: `applications/gam-reports-mcp/.python-version`

**Step 1: Create directory structure**

```bash
mkdir -p applications/gam-reports-mcp/{config/templates,models,endpoints,core}
touch applications/gam-reports-mcp/{config,models,endpoints,core}/__init__.py
```

**Step 2: Create pyproject.toml**

```toml
[project]
name = "gam-reports-mcp"
version = "1.0.0"
description = "Standalone MCP server for Google Ad Manager report management"
requires-python = ">=3.11"
dependencies = [
    "fastmcp>=2.0.0",
    "aiohttp>=3.9.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "google-auth>=2.0.0",
    "pyyaml>=6.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Step 3: Create .python-version**

```
3.11
```

**Step 4: Initialize with uv**

Run: `cd applications/gam-reports-mcp && uv sync`
Expected: Dependencies installed, uv.lock created

**Step 5: Commit**

```bash
git add applications/gam-reports-mcp/
git commit -m "feat(gam-reports-mcp): scaffold project structure"
```

---

## Task 2: Error Models

**Files:**
- Create: `applications/gam-reports-mcp/models/errors.py`
- Create: `applications/gam-reports-mcp/tests/__init__.py`
- Create: `applications/gam-reports-mcp/tests/test_models.py`

**Step 1: Write failing test for error models**

```python
# tests/test_models.py
import pytest
from models.errors import APIError, AuthenticationError, QuotaExceededError, ValidationError


def test_api_error_has_message():
    error = APIError("Something went wrong")
    assert str(error) == "Something went wrong"
    assert error.message == "Something went wrong"


def test_authentication_error_inherits_api_error():
    error = AuthenticationError("Invalid token")
    assert isinstance(error, APIError)


def test_quota_exceeded_has_retry_after():
    error = QuotaExceededError("Rate limited", retry_after=60)
    assert error.retry_after == 60


def test_validation_error_has_field():
    error = ValidationError("Invalid dimension", field="dimensions")
    assert error.field == "dimensions"
```

**Step 2: Run test to verify it fails**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_models.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'models'"

**Step 3: Write implementation**

```python
# models/errors.py
"""Custom exceptions for GAM Reports MCP."""


class APIError(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(APIError):
    """Authentication failed."""

    pass


class QuotaExceededError(APIError):
    """Rate limit exceeded."""

    def __init__(self, message: str, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(message, status_code=429)


class ValidationError(APIError):
    """Validation error."""

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message, status_code=400)
```

**Step 4: Update models/__init__.py**

```python
# models/__init__.py
from .errors import APIError, AuthenticationError, QuotaExceededError, ValidationError

__all__ = ["APIError", "AuthenticationError", "QuotaExceededError", "ValidationError"]
```

**Step 5: Run test to verify it passes**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_models.py -v`
Expected: PASS (4 tests)

**Step 6: Commit**

```bash
git add applications/gam-reports-mcp/models/ applications/gam-reports-mcp/tests/
git commit -m "feat(gam-reports-mcp): add error models"
```

---

## Task 3: Dimension Models

**Files:**
- Create: `applications/gam-reports-mcp/models/dimensions.py`
- Modify: `applications/gam-reports-mcp/tests/test_models.py`

**Step 1: Write failing test**

```python
# Add to tests/test_models.py
from models.dimensions import Dimension, DimensionCategory, ALLOWED_DIMENSIONS


def test_dimension_category_enum():
    assert DimensionCategory.TIME == "time"
    assert DimensionCategory.INVENTORY == "inventory"


def test_dimension_model():
    dim = Dimension(
        name="DATE",
        category=DimensionCategory.TIME,
        description="Daily granularity",
        use_case="Daily performance trends",
        compatible_with=["TOTAL_IMPRESSIONS"],
    )
    assert dim.name == "DATE"
    assert dim.category == DimensionCategory.TIME


def test_allowed_dimensions_contains_date():
    assert "DATE" in ALLOWED_DIMENSIONS
    assert ALLOWED_DIMENSIONS["DATE"].category == DimensionCategory.TIME


def test_allowed_dimensions_contains_ad_unit_name():
    assert "AD_UNIT_NAME" in ALLOWED_DIMENSIONS
    assert ALLOWED_DIMENSIONS["AD_UNIT_NAME"].category == DimensionCategory.INVENTORY
```

**Step 2: Run test to verify it fails**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_models.py::test_dimension_category_enum -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write implementation**

```python
# models/dimensions.py
"""Curated dimension definitions for GAM Reports."""

from enum import Enum
from pydantic import BaseModel, Field


class DimensionCategory(str, Enum):
    """Categories for dimensions."""

    TIME = "time"
    INVENTORY = "inventory"
    ADVERTISER = "advertiser"
    GEOGRAPHY = "geography"
    DEVICE = "device"


class Dimension(BaseModel):
    """A curated dimension with domain context."""

    name: str = Field(description="GAM API dimension name")
    category: DimensionCategory
    description: str = Field(description="What this dimension represents")
    use_case: str = Field(description="When to use this dimension")
    compatible_with: list[str] = Field(
        default_factory=list, description="Metrics that work well with this"
    )


# Curated allowlist - add your dimensions here
ALLOWED_DIMENSIONS: dict[str, Dimension] = {
    "DATE": Dimension(
        name="DATE",
        category=DimensionCategory.TIME,
        description="Daily granularity",
        use_case="Daily performance trends",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    "WEEK": Dimension(
        name="WEEK",
        category=DimensionCategory.TIME,
        description="Weekly aggregation",
        use_case="Weekly reporting",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
    ),
    "MONTH": Dimension(
        name="MONTH",
        category=DimensionCategory.TIME,
        description="Monthly aggregation",
        use_case="Monthly reporting",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_REVENUE"],
    ),
    "AD_UNIT_NAME": Dimension(
        name="AD_UNIT_NAME",
        category=DimensionCategory.INVENTORY,
        description="Ad placement names",
        use_case="Performance by placement",
        compatible_with=["AD_REQUESTS", "MATCHED_REQUESTS", "FILL_RATE"],
    ),
    "AD_UNIT_CODE": Dimension(
        name="AD_UNIT_CODE",
        category=DimensionCategory.INVENTORY,
        description="Ad unit codes",
        use_case="Technical integration analysis",
        compatible_with=["AD_REQUESTS", "MATCHED_REQUESTS"],
    ),
    "ADVERTISER_NAME": Dimension(
        name="ADVERTISER_NAME",
        category=DimensionCategory.ADVERTISER,
        description="Advertiser display names",
        use_case="Revenue by advertiser",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "ORDER_NAME": Dimension(
        name="ORDER_NAME",
        category=DimensionCategory.ADVERTISER,
        description="Order/campaign names",
        use_case="Campaign performance",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
    ),
    "COUNTRY_NAME": Dimension(
        name="COUNTRY_NAME",
        category=DimensionCategory.GEOGRAPHY,
        description="Country name",
        use_case="Geographic performance",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
    ),
    "DEVICE_CATEGORY_NAME": Dimension(
        name="DEVICE_CATEGORY_NAME",
        category=DimensionCategory.DEVICE,
        description="Device type (Desktop, Mobile, Tablet)",
        use_case="Device performance analysis",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
}
```

**Step 4: Update models/__init__.py**

```python
# models/__init__.py
from .errors import APIError, AuthenticationError, QuotaExceededError, ValidationError
from .dimensions import Dimension, DimensionCategory, ALLOWED_DIMENSIONS

__all__ = [
    "APIError",
    "AuthenticationError",
    "QuotaExceededError",
    "ValidationError",
    "Dimension",
    "DimensionCategory",
    "ALLOWED_DIMENSIONS",
]
```

**Step 5: Run test to verify it passes**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_models.py -v`
Expected: PASS (8 tests)

**Step 6: Commit**

```bash
git add applications/gam-reports-mcp/models/
git commit -m "feat(gam-reports-mcp): add dimension models with curated allowlist"
```

---

## Task 4: Metric Models

**Files:**
- Create: `applications/gam-reports-mcp/models/metrics.py`
- Modify: `applications/gam-reports-mcp/tests/test_models.py`

**Step 1: Write failing test**

```python
# Add to tests/test_models.py
from models.metrics import Metric, MetricCategory, ALLOWED_METRICS


def test_metric_category_enum():
    assert MetricCategory.DELIVERY == "delivery"
    assert MetricCategory.REVENUE == "revenue"


def test_metric_model():
    metric = Metric(
        name="TOTAL_IMPRESSIONS",
        category=MetricCategory.DELIVERY,
        description="Total ad impressions served",
        use_case="Volume analysis",
    )
    assert metric.name == "TOTAL_IMPRESSIONS"


def test_allowed_metrics_contains_impressions():
    assert "TOTAL_IMPRESSIONS" in ALLOWED_METRICS
    assert ALLOWED_METRICS["TOTAL_IMPRESSIONS"].category == MetricCategory.DELIVERY


def test_allowed_metrics_contains_revenue():
    assert "TOTAL_CPM_AND_CPC_REVENUE" in ALLOWED_METRICS
    assert ALLOWED_METRICS["TOTAL_CPM_AND_CPC_REVENUE"].category == MetricCategory.REVENUE
```

**Step 2: Run test to verify it fails**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_models.py::test_metric_category_enum -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# models/metrics.py
"""Curated metric definitions for GAM Reports."""

from enum import Enum
from pydantic import BaseModel, Field


class MetricCategory(str, Enum):
    """Categories for metrics."""

    DELIVERY = "delivery"
    REVENUE = "revenue"
    INVENTORY = "inventory"
    ENGAGEMENT = "engagement"


class Metric(BaseModel):
    """A curated metric with domain context."""

    name: str = Field(description="GAM API metric name")
    category: MetricCategory
    description: str = Field(description="What this metric represents")
    use_case: str = Field(description="When to use this metric")


# Curated allowlist - add your metrics here
ALLOWED_METRICS: dict[str, Metric] = {
    "TOTAL_IMPRESSIONS": Metric(
        name="TOTAL_IMPRESSIONS",
        category=MetricCategory.DELIVERY,
        description="Total ad impressions served",
        use_case="Volume analysis",
    ),
    "TOTAL_CLICKS": Metric(
        name="TOTAL_CLICKS",
        category=MetricCategory.DELIVERY,
        description="Total clicks on ads",
        use_case="Engagement analysis",
    ),
    "TOTAL_CTR": Metric(
        name="TOTAL_CTR",
        category=MetricCategory.ENGAGEMENT,
        description="Click-through rate",
        use_case="Ad effectiveness",
    ),
    "TOTAL_CPM_AND_CPC_REVENUE": Metric(
        name="TOTAL_CPM_AND_CPC_REVENUE",
        category=MetricCategory.REVENUE,
        description="Combined CPM and CPC revenue",
        use_case="Total revenue analysis",
    ),
    "TOTAL_ECPM": Metric(
        name="TOTAL_ECPM",
        category=MetricCategory.REVENUE,
        description="Effective CPM",
        use_case="Yield optimization",
    ),
    "AD_REQUESTS": Metric(
        name="AD_REQUESTS",
        category=MetricCategory.INVENTORY,
        description="Total ad requests",
        use_case="Demand analysis",
    ),
    "MATCHED_REQUESTS": Metric(
        name="MATCHED_REQUESTS",
        category=MetricCategory.INVENTORY,
        description="Requests matched with ads",
        use_case="Fill analysis",
    ),
    "FILL_RATE": Metric(
        name="FILL_RATE",
        category=MetricCategory.INVENTORY,
        description="Percentage of requests filled",
        use_case="Inventory efficiency",
    ),
}
```

**Step 4: Update models/__init__.py**

```python
# models/__init__.py
from .errors import APIError, AuthenticationError, QuotaExceededError, ValidationError
from .dimensions import Dimension, DimensionCategory, ALLOWED_DIMENSIONS
from .metrics import Metric, MetricCategory, ALLOWED_METRICS

__all__ = [
    "APIError",
    "AuthenticationError",
    "QuotaExceededError",
    "ValidationError",
    "Dimension",
    "DimensionCategory",
    "ALLOWED_DIMENSIONS",
    "Metric",
    "MetricCategory",
    "ALLOWED_METRICS",
]
```

**Step 5: Run test to verify it passes**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_models.py -v`
Expected: PASS (12 tests)

**Step 6: Commit**

```bash
git add applications/gam-reports-mcp/models/
git commit -m "feat(gam-reports-mcp): add metric models with curated allowlist"
```

---

## Task 5: Filter Models

**Files:**
- Create: `applications/gam-reports-mcp/models/filters.py`
- Modify: `applications/gam-reports-mcp/tests/test_models.py`

**Step 1: Write failing test**

```python
# Add to tests/test_models.py
from datetime import date
from models.filters import DateRangeFilter, DomainFilter, AdStrategyFilter


def test_date_range_filter():
    f = DateRangeFilter(start_date=date(2024, 1, 1), end_date=date(2024, 1, 31))
    assert f.start_date == date(2024, 1, 1)
    assert f.end_date == date(2024, 1, 31)


def test_date_range_from_strings():
    f = DateRangeFilter(start_date="2024-01-01", end_date="2024-01-31")
    assert f.start_date == date(2024, 1, 1)


def test_domain_filter():
    f = DomainFilter(domains=["example.com", "m.example.com"])
    assert len(f.domains) == 2


def test_ad_strategy_filter():
    f = AdStrategyFilter(strategy="direct_sold")
    assert f.strategy == "direct_sold"
```

**Step 2: Run test to verify it fails**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_models.py::test_date_range_filter -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# models/filters.py
"""Filter models for GAM Reports."""

from datetime import date
from typing import Literal
from pydantic import BaseModel, Field


class DateRangeFilter(BaseModel):
    """Date range filter for reports."""

    start_date: date
    end_date: date


class DomainFilter(BaseModel):
    """Filter by domains."""

    domains: list[str] = Field(description="Filter by your domains")


class AppFilter(BaseModel):
    """Filter by mobile apps."""

    app_ids: list[str] = Field(description="Your app bundle IDs")


class AdStrategyFilter(BaseModel):
    """Filter by ad strategy."""

    strategy: Literal["direct_sold", "programmatic", "house"]
```

**Step 4: Update models/__init__.py**

```python
# models/__init__.py
from .errors import APIError, AuthenticationError, QuotaExceededError, ValidationError
from .dimensions import Dimension, DimensionCategory, ALLOWED_DIMENSIONS
from .metrics import Metric, MetricCategory, ALLOWED_METRICS
from .filters import DateRangeFilter, DomainFilter, AppFilter, AdStrategyFilter

__all__ = [
    "APIError",
    "AuthenticationError",
    "QuotaExceededError",
    "ValidationError",
    "Dimension",
    "DimensionCategory",
    "ALLOWED_DIMENSIONS",
    "Metric",
    "MetricCategory",
    "ALLOWED_METRICS",
    "DateRangeFilter",
    "DomainFilter",
    "AppFilter",
    "AdStrategyFilter",
]
```

**Step 5: Run test to verify it passes**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_models.py -v`
Expected: PASS (16 tests)

**Step 6: Commit**

```bash
git add applications/gam-reports-mcp/models/
git commit -m "feat(gam-reports-mcp): add filter models"
```

---

## Task 6: Knowledge Models (Domain Context)

**Files:**
- Create: `applications/gam-reports-mcp/models/knowledge.py`
- Modify: `applications/gam-reports-mcp/tests/test_models.py`

**Step 1: Write failing test**

```python
# Add to tests/test_models.py
from models.knowledge import Domain, App, AdStrategy, ReportTemplate


def test_domain_model():
    d = Domain(name="example.com", ad_units=["homepage_leaderboard", "sidebar_mpu"])
    assert d.name == "example.com"
    assert len(d.ad_units) == 2


def test_app_model():
    app = App(name="Example iOS", bundle_id="com.example.ios", ad_units=["app_banner"])
    assert app.bundle_id == "com.example.ios"


def test_ad_strategy_model():
    s = AdStrategy(
        name="direct_sold",
        description="Guaranteed campaigns",
        typical_dimensions=["ADVERTISER_NAME", "ORDER_NAME"],
        typical_metrics=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE"],
    )
    assert s.name == "direct_sold"


def test_report_template():
    t = ReportTemplate(
        name="delivery",
        description="Standard delivery report",
        dimensions=["DATE", "AD_UNIT_NAME"],
        metrics=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
    )
    assert t.name == "delivery"
```

**Step 2: Run test to verify it fails**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_models.py::test_domain_model -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# models/knowledge.py
"""Domain knowledge models for company context."""

from pydantic import BaseModel, Field


class Domain(BaseModel):
    """A known domain in your network."""

    name: str
    ad_units: list[str] = Field(default_factory=list)


class App(BaseModel):
    """A known mobile app in your network."""

    name: str
    bundle_id: str
    ad_units: list[str] = Field(default_factory=list)


class AdStrategy(BaseModel):
    """An ad monetization strategy."""

    name: str
    description: str
    typical_dimensions: list[str] = Field(default_factory=list)
    typical_metrics: list[str] = Field(default_factory=list)


class ReportTemplate(BaseModel):
    """A predefined report template."""

    name: str
    description: str
    dimensions: list[str]
    metrics: list[str]
    default_date_range_days: int = 7


# Default knowledge - customize for your network
KNOWN_DOMAINS: list[Domain] = []
KNOWN_APPS: list[App] = []
AD_STRATEGIES: list[AdStrategy] = [
    AdStrategy(
        name="direct_sold",
        description="Guaranteed campaigns sold directly to advertisers",
        typical_dimensions=["ADVERTISER_NAME", "ORDER_NAME", "DATE"],
        typical_metrics=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    AdStrategy(
        name="programmatic",
        description="Programmatic demand via exchanges",
        typical_dimensions=["DATE", "AD_UNIT_NAME"],
        typical_metrics=["TOTAL_IMPRESSIONS", "TOTAL_ECPM", "FILL_RATE"],
    ),
    AdStrategy(
        name="house",
        description="House ads for unsold inventory",
        typical_dimensions=["DATE", "AD_UNIT_NAME"],
        typical_metrics=["TOTAL_IMPRESSIONS"],
    ),
]
REPORT_TEMPLATES: list[ReportTemplate] = [
    ReportTemplate(
        name="delivery",
        description="Standard delivery report with impressions and clicks",
        dimensions=["DATE", "AD_UNIT_NAME"],
        metrics=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    ReportTemplate(
        name="inventory",
        description="Inventory health and fill rate analysis",
        dimensions=["DATE", "AD_UNIT_NAME"],
        metrics=["AD_REQUESTS", "MATCHED_REQUESTS", "FILL_RATE"],
    ),
    ReportTemplate(
        name="revenue",
        description="Revenue analysis by advertiser",
        dimensions=["DATE", "ADVERTISER_NAME"],
        metrics=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE", "TOTAL_ECPM"],
    ),
]
```

**Step 4: Update models/__init__.py**

```python
# models/__init__.py
from .errors import APIError, AuthenticationError, QuotaExceededError, ValidationError
from .dimensions import Dimension, DimensionCategory, ALLOWED_DIMENSIONS
from .metrics import Metric, MetricCategory, ALLOWED_METRICS
from .filters import DateRangeFilter, DomainFilter, AppFilter, AdStrategyFilter
from .knowledge import (
    Domain,
    App,
    AdStrategy,
    ReportTemplate,
    KNOWN_DOMAINS,
    KNOWN_APPS,
    AD_STRATEGIES,
    REPORT_TEMPLATES,
)

__all__ = [
    "APIError",
    "AuthenticationError",
    "QuotaExceededError",
    "ValidationError",
    "Dimension",
    "DimensionCategory",
    "ALLOWED_DIMENSIONS",
    "Metric",
    "MetricCategory",
    "ALLOWED_METRICS",
    "DateRangeFilter",
    "DomainFilter",
    "AppFilter",
    "AdStrategyFilter",
    "Domain",
    "App",
    "AdStrategy",
    "ReportTemplate",
    "KNOWN_DOMAINS",
    "KNOWN_APPS",
    "AD_STRATEGIES",
    "REPORT_TEMPLATES",
]
```

**Step 5: Run test to verify it passes**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_models.py -v`
Expected: PASS (20 tests)

**Step 6: Commit**

```bash
git add applications/gam-reports-mcp/models/
git commit -m "feat(gam-reports-mcp): add knowledge models for domain context"
```

---

## Task 7: Report Request/Response Models

**Files:**
- Create: `applications/gam-reports-mcp/models/reports.py`
- Modify: `applications/gam-reports-mcp/tests/test_models.py`

**Step 1: Write failing test**

```python
# Add to tests/test_models.py
from models.reports import CreateReportRequest, ReportResponse


def test_create_report_request():
    req = CreateReportRequest(
        display_name="Test Report",
        dimensions=["DATE", "AD_UNIT_NAME"],
        metrics=["TOTAL_IMPRESSIONS"],
        start_date="2024-01-01",
        end_date="2024-01-31",
    )
    assert req.display_name == "Test Report"
    assert len(req.dimensions) == 2


def test_create_report_request_to_gam_format():
    req = CreateReportRequest(
        dimensions=["DATE"],
        metrics=["TOTAL_IMPRESSIONS"],
        start_date="2024-01-01",
        end_date="2024-01-31",
    )
    gam_format = req.to_gam_format()
    assert "reportDefinition" in gam_format
    assert gam_format["reportDefinition"]["dimensions"] == ["DATE"]


def test_report_response():
    resp = ReportResponse(
        name="networks/123/reports/456",
        report_id="456",
        display_name="Test Report",
        state="COMPLETED",
    )
    assert resp.report_id == "456"
    assert resp.state == "COMPLETED"
```

**Step 2: Run test to verify it fails**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_models.py::test_create_report_request -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# models/reports.py
"""Report request and response models."""

from datetime import date
from typing import Any
from pydantic import BaseModel, Field


class CreateReportRequest(BaseModel):
    """Request to create a new report."""

    display_name: str | None = None
    dimensions: list[str]
    metrics: list[str]
    start_date: date | str
    end_date: date | str
    filters: dict[str, Any] | None = None

    def to_gam_format(self) -> dict[str, Any]:
        """Convert to GAM REST API format."""
        start = (
            self.start_date
            if isinstance(self.start_date, str)
            else self.start_date.isoformat()
        )
        end = (
            self.end_date
            if isinstance(self.end_date, str)
            else self.end_date.isoformat()
        )

        report_def: dict[str, Any] = {
            "dimensions": self.dimensions,
            "metrics": self.metrics,
            "dateRange": {
                "startDate": {"year": int(start[:4]), "month": int(start[5:7]), "day": int(start[8:10])},
                "endDate": {"year": int(end[:4]), "month": int(end[5:7]), "day": int(end[8:10])},
            },
        }

        if self.filters:
            report_def["filters"] = self.filters

        result: dict[str, Any] = {"reportDefinition": report_def}

        if self.display_name:
            result["displayName"] = self.display_name

        return result


class ReportResponse(BaseModel):
    """Response from report operations."""

    name: str = Field(description="Resource name: networks/{network}/reports/{id}")
    report_id: str = Field(description="The report ID")
    display_name: str | None = None
    state: str = Field(default="UNKNOWN", description="Report state")

    @classmethod
    def from_gam_response(cls, data: dict[str, Any]) -> "ReportResponse":
        """Create from GAM API response."""
        name = data.get("name", "")
        # Extract report_id from name: networks/123/reports/456 -> 456
        report_id = name.split("/")[-1] if name else ""
        return cls(
            name=name,
            report_id=report_id,
            display_name=data.get("displayName"),
            state=data.get("state", "UNKNOWN"),
        )


class FetchRowsResponse(BaseModel):
    """Response from fetching report rows."""

    rows: list[dict[str, Any]] = Field(default_factory=list)
    next_page_token: str | None = None
    total_row_count: int = 0
```

**Step 4: Update models/__init__.py to include report models**

```python
# Add to models/__init__.py imports
from .reports import CreateReportRequest, ReportResponse, FetchRowsResponse

# Add to __all__
__all__ = [
    # ... existing exports ...
    "CreateReportRequest",
    "ReportResponse",
    "FetchRowsResponse",
]
```

**Step 5: Run test to verify it passes**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_models.py -v`
Expected: PASS (23 tests)

**Step 6: Commit**

```bash
git add applications/gam-reports-mcp/models/
git commit -m "feat(gam-reports-mcp): add report request/response models"
```

---

## Task 8: Auth Module

**Files:**
- Create: `applications/gam-reports-mcp/core/auth.py`
- Create: `applications/gam-reports-mcp/tests/test_core.py`

**Step 1: Write failing test**

```python
# tests/test_core.py
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from core.auth import GAMAuth, AuthConfig


def test_auth_config_model():
    config = AuthConfig(
        client_id="test-client-id",
        client_secret="test-secret",
        refresh_token="test-refresh",
        network_code="123456",
    )
    assert config.client_id == "test-client-id"
    assert config.network_code == "123456"


def test_gam_auth_loads_config(tmp_path):
    config_file = tmp_path / "googleads.yaml"
    config_file.write_text("""
ad_manager:
  client_id: test-client-id
  client_secret: test-secret
  refresh_token: test-refresh
  network_code: "123456"
""")

    auth = GAMAuth(config_path=config_file)
    assert auth.config.client_id == "test-client-id"
    assert auth.network_code == "123456"


def test_gam_auth_network_code_property(tmp_path):
    config_file = tmp_path / "googleads.yaml"
    config_file.write_text("""
ad_manager:
  client_id: test-client-id
  client_secret: test-secret
  refresh_token: test-refresh
  network_code: "789"
""")

    auth = GAMAuth(config_path=config_file)
    assert auth.network_code == "789"
```

**Step 2: Run test to verify it fails**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_core.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'core'"

**Step 3: Write implementation**

```python
# core/auth.py
"""Standalone OAuth2 authentication for GAM REST API."""

from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


class AuthConfig(BaseModel):
    """Authentication configuration."""

    client_id: str
    client_secret: str
    refresh_token: str
    network_code: str


class GAMAuth:
    """Standalone OAuth2 authentication for GAM Reports MCP."""

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or Path.home() / ".googleads.yaml"
        self._credentials: Credentials | None = None
        self._config: AuthConfig | None = None

    @property
    def config(self) -> AuthConfig:
        """Load and cache configuration."""
        if self._config is None:
            data = yaml.safe_load(self.config_path.read_text())
            ad_manager: dict[str, Any] = data.get("ad_manager", {})
            self._config = AuthConfig(
                client_id=ad_manager["client_id"],
                client_secret=ad_manager["client_secret"],
                refresh_token=ad_manager["refresh_token"],
                network_code=str(ad_manager["network_code"]),
            )
        return self._config

    @property
    def network_code(self) -> str:
        """Get network code from configuration."""
        return self.config.network_code

    def get_credentials(self) -> Credentials:
        """Get OAuth2 credentials, refreshing if needed."""
        if self._credentials is None:
            self._credentials = Credentials(
                None,
                refresh_token=self.config.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
            )
            self._credentials.refresh(Request())

        if self._credentials.expired:
            self._credentials.refresh(Request())

        return self._credentials
```

**Step 4: Update core/__init__.py**

```python
# core/__init__.py
from .auth import GAMAuth, AuthConfig

__all__ = ["GAMAuth", "AuthConfig"]
```

**Step 5: Run test to verify it passes**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_core.py -v`
Expected: PASS (3 tests)

**Step 6: Commit**

```bash
git add applications/gam-reports-mcp/core/
git commit -m "feat(gam-reports-mcp): add standalone auth module"
```

---

## Task 9: Async Client Module

**Files:**
- Create: `applications/gam-reports-mcp/core/client.py`
- Modify: `applications/gam-reports-mcp/tests/test_core.py`

**Step 1: Write failing test**

```python
# Add to tests/test_core.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.client import GAMClient


@pytest.fixture
def mock_auth():
    auth = MagicMock()
    auth.network_code = "123456"
    creds = MagicMock()
    creds.token = "test-token"
    creds.expired = False
    auth.get_credentials.return_value = creds
    return auth


@pytest.mark.asyncio
async def test_gam_client_context_manager(mock_auth):
    async with GAMClient(mock_auth) as client:
        assert client.auth == mock_auth
    # Session should be closed after context


@pytest.mark.asyncio
async def test_gam_client_get_builds_correct_url(mock_auth):
    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": "test"})
        mock_session.request.return_value.__aenter__.return_value = mock_response
        mock_session.closed = False
        mock_session_class.return_value = mock_session

        client = GAMClient(mock_auth)
        client._session = mock_session

        result = await client.get("/networks/123/reports")

        assert result == {"data": "test"}
```

**Step 2: Run test to verify it fails**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_core.py::test_gam_client_context_manager -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# core/client.py
"""Async REST client for GAM API using aiohttp."""

import asyncio
import logging
from typing import Any

import aiohttp

from core.auth import GAMAuth
from models.errors import APIError, AuthenticationError, QuotaExceededError

logger = logging.getLogger(__name__)

API_BASE_URL = "https://admanager.googleapis.com/v1"


class GAMClient:
    """Async GAM REST client with connection pooling and retry logic."""

    def __init__(self, auth: GAMAuth):
        self.auth = auth
        self._session: aiohttp.ClientSession | None = None
        self._connector: aiohttp.TCPConnector | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create async session with connection pooling."""
        if self._session is None or self._session.closed:
            if self._connector is None or self._connector.closed:
                self._connector = aiohttp.TCPConnector(
                    limit=100,
                    limit_per_host=10,
                    keepalive_timeout=30,
                )

            credentials = self.auth.get_credentials()
            self._session = aiohttp.ClientSession(
                connector=self._connector,
                headers={
                    "Authorization": f"Bearer {credentials.token}",
                    "Content-Type": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=300, connect=30),
            )
        return self._session

    async def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        retries: int = 3,
    ) -> dict[str, Any]:
        """Make request with retry and error handling."""
        session = await self._get_session()
        url = f"{API_BASE_URL}{path}"

        for attempt in range(retries):
            try:
                async with session.request(method, url, json=json) as response:
                    if response.status == 401 and attempt < retries - 1:
                        # Refresh token and update session
                        credentials = self.auth.get_credentials()
                        session.headers["Authorization"] = f"Bearer {credentials.token}"
                        continue

                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        if attempt < retries - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        raise QuotaExceededError("Rate limited", retry_after=retry_after)

                    if response.status == 401:
                        raise AuthenticationError("Authentication failed")

                    if response.status >= 400:
                        error_data = await response.json()
                        error_msg = error_data.get("error", {}).get("message", "Unknown error")
                        raise APIError(error_msg, status_code=response.status)

                    if response.status == 204:
                        return {}
                    return await response.json()

            except aiohttp.ClientError as e:
                if attempt == retries - 1:
                    raise APIError(f"HTTP client error: {e}")
                await asyncio.sleep(2**attempt)

        raise APIError("Max retries exceeded")

    async def post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        """POST request."""
        return await self._request("POST", path, json)

    async def get(self, path: str) -> dict[str, Any]:
        """GET request."""
        return await self._request("GET", path)

    async def patch(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        """PATCH request."""
        return await self._request("PATCH", path, json)

    async def delete(self, path: str) -> None:
        """DELETE request."""
        await self._request("DELETE", path)

    async def close(self) -> None:
        """Close session and connector."""
        if self._session and not self._session.closed:
            await self._session.close()
        if self._connector and not self._connector.closed:
            await self._connector.close()

    async def __aenter__(self) -> "GAMClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
```

**Step 4: Update core/__init__.py**

```python
# core/__init__.py
from .auth import GAMAuth, AuthConfig
from .client import GAMClient

__all__ = ["GAMAuth", "AuthConfig", "GAMClient"]
```

**Step 5: Run test to verify it passes**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_core.py -v`
Expected: PASS (5 tests)

**Step 6: Commit**

```bash
git add applications/gam-reports-mcp/core/
git commit -m "feat(gam-reports-mcp): add async GAM client with connection pooling"
```

---

## Task 10: Settings Module

**Files:**
- Create: `applications/gam-reports-mcp/config/settings.py`
- Create: `applications/gam-reports-mcp/tests/test_config.py`

**Step 1: Write failing test**

```python
# tests/test_config.py
import pytest
from pathlib import Path
from config.settings import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.mcp_transport == "stdio"
    assert settings.mcp_port == 8080
    assert settings.auth_enabled is False


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    monkeypatch.setenv("MCP_PORT", "9000")
    monkeypatch.setenv("MCP_AUTH_ENABLED", "true")

    settings = Settings()
    assert settings.mcp_transport == "http"
    assert settings.mcp_port == 9000
    assert settings.auth_enabled is True
```

**Step 2: Run test to verify it fails**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_config.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# config/settings.py
"""Application settings from environment."""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # GAM Configuration
    network_code: str = Field(default="", alias="GAM_NETWORK_CODE")
    credentials_path: Path = Field(
        default=Path.home() / ".googleads.yaml",
        alias="GOOGLE_ADS_YAML",
    )

    # MCP Server
    mcp_transport: str = Field(default="stdio", alias="MCP_TRANSPORT")
    mcp_port: int = Field(default=8080, alias="MCP_PORT")

    # JWT Auth (for Cloud Run)
    auth_enabled: bool = Field(default=False, alias="MCP_AUTH_ENABLED")
    jwt_secret: str = Field(default="", alias="JWT_SECRET")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
```

**Step 4: Update config/__init__.py**

```python
# config/__init__.py
from .settings import Settings, settings

__all__ = ["Settings", "settings"]
```

**Step 5: Run test to verify it passes**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_config.py -v`
Expected: PASS (2 tests)

**Step 6: Commit**

```bash
git add applications/gam-reports-mcp/config/
git commit -m "feat(gam-reports-mcp): add settings module with pydantic-settings"
```

---

## Task 11: Create Endpoint

**Files:**
- Create: `applications/gam-reports-mcp/endpoints/create.py`
- Create: `applications/gam-reports-mcp/tests/test_endpoints.py`

**Step 1: Write failing test**

```python
# tests/test_endpoints.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from endpoints.create import create_report
from models.reports import CreateReportRequest


@pytest.fixture
def mock_client():
    client = AsyncMock()
    client.post.return_value = {
        "name": "networks/123/reports/456",
        "displayName": "Test Report",
        "state": "COMPLETED",
    }
    return client


@pytest.mark.asyncio
async def test_create_report_success(mock_client):
    request = CreateReportRequest(
        display_name="Test Report",
        dimensions=["DATE"],
        metrics=["TOTAL_IMPRESSIONS"],
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    result = await create_report(mock_client, "123", request)

    assert result.report_id == "456"
    assert result.name == "networks/123/reports/456"


@pytest.mark.asyncio
async def test_create_report_validates_dimensions(mock_client):
    request = CreateReportRequest(
        dimensions=["INVALID_DIMENSION"],
        metrics=["TOTAL_IMPRESSIONS"],
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    with pytest.raises(ValueError, match="not in curated allowlist"):
        await create_report(mock_client, "123", request)


@pytest.mark.asyncio
async def test_create_report_validates_metrics(mock_client):
    request = CreateReportRequest(
        dimensions=["DATE"],
        metrics=["INVALID_METRIC"],
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    with pytest.raises(ValueError, match="not in curated allowlist"):
        await create_report(mock_client, "123", request)
```

**Step 2: Run test to verify it fails**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_endpoints.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# endpoints/create.py
"""Create report endpoint."""

from core.client import GAMClient
from models.reports import CreateReportRequest, ReportResponse
from models.dimensions import ALLOWED_DIMENSIONS
from models.metrics import ALLOWED_METRICS


async def create_report(
    client: GAMClient,
    network_code: str,
    request: CreateReportRequest,
) -> ReportResponse:
    """
    POST /networks/{network}/reports

    Creates a new report, validating dimensions/metrics against curated allowlist.
    """
    # Validate dimensions
    for dim in request.dimensions:
        if dim not in ALLOWED_DIMENSIONS:
            raise ValueError(f"Dimension '{dim}' not in curated allowlist")

    # Validate metrics
    for metric in request.metrics:
        if metric not in ALLOWED_METRICS:
            raise ValueError(f"Metric '{metric}' not in curated allowlist")

    response = await client.post(
        f"/networks/{network_code}/reports",
        json=request.to_gam_format(),
    )
    return ReportResponse.from_gam_response(response)
```

**Step 4: Update endpoints/__init__.py**

```python
# endpoints/__init__.py
from .create import create_report

__all__ = ["create_report"]
```

**Step 5: Run test to verify it passes**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_endpoints.py -v`
Expected: PASS (3 tests)

**Step 6: Commit**

```bash
git add applications/gam-reports-mcp/endpoints/
git commit -m "feat(gam-reports-mcp): add create report endpoint with validation"
```

---

## Task 12: Run Endpoint

**Files:**
- Create: `applications/gam-reports-mcp/endpoints/run.py`
- Modify: `applications/gam-reports-mcp/tests/test_endpoints.py`

**Step 1: Write failing test**

```python
# Add to tests/test_endpoints.py
from endpoints.run import run_report


@pytest.mark.asyncio
async def test_run_report_returns_operation_name(mock_client):
    mock_client.post.return_value = {
        "name": "networks/123/operations/reports/runs/789",
        "done": False,
    }

    result = await run_report(mock_client, "123", "456")

    assert result == "networks/123/operations/reports/runs/789"
    mock_client.post.assert_called_with("/networks/123/reports/456:run", json=None)
```

**Step 2: Run test to verify it fails**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_endpoints.py::test_run_report_returns_operation_name -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# endpoints/run.py
"""Run report endpoint."""

from core.client import GAMClient


async def run_report(
    client: GAMClient,
    network_code: str,
    report_id: str,
) -> str:
    """
    POST /networks/{network}/reports/{id}:run

    Triggers report execution and returns the operation name for tracking.
    """
    response = await client.post(
        f"/networks/{network_code}/reports/{report_id}:run",
        json=None,
    )
    return response.get("name", "")
```

**Step 4: Update endpoints/__init__.py**

```python
# endpoints/__init__.py
from .create import create_report
from .run import run_report

__all__ = ["create_report", "run_report"]
```

**Step 5: Run test to verify it passes**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_endpoints.py -v`
Expected: PASS (4 tests)

**Step 6: Commit**

```bash
git add applications/gam-reports-mcp/endpoints/
git commit -m "feat(gam-reports-mcp): add run report endpoint"
```

---

## Task 13: Remaining Endpoints (get, list, update, delete, fetch, operations)

**Files:**
- Create: `applications/gam-reports-mcp/endpoints/get.py`
- Create: `applications/gam-reports-mcp/endpoints/list.py`
- Create: `applications/gam-reports-mcp/endpoints/update.py`
- Create: `applications/gam-reports-mcp/endpoints/delete.py`
- Create: `applications/gam-reports-mcp/endpoints/fetch.py`
- Create: `applications/gam-reports-mcp/endpoints/operations.py`

**Step 1: Create all endpoint files**

```python
# endpoints/get.py
"""Get report endpoint."""

from core.client import GAMClient
from models.reports import ReportResponse


async def get_report(
    client: GAMClient,
    network_code: str,
    report_id: str,
) -> ReportResponse:
    """GET /networks/{network}/reports/{id}"""
    response = await client.get(f"/networks/{network_code}/reports/{report_id}")
    return ReportResponse.from_gam_response(response)
```

```python
# endpoints/list.py
"""List reports endpoint."""

from typing import Any
from core.client import GAMClient


async def list_reports(
    client: GAMClient,
    network_code: str,
    page_size: int = 100,
    page_token: str | None = None,
) -> dict[str, Any]:
    """GET /networks/{network}/reports"""
    path = f"/networks/{network_code}/reports?pageSize={page_size}"
    if page_token:
        path += f"&pageToken={page_token}"
    return await client.get(path)
```

```python
# endpoints/update.py
"""Update report endpoint."""

from typing import Any
from core.client import GAMClient
from models.reports import ReportResponse


async def update_report(
    client: GAMClient,
    network_code: str,
    report_id: str,
    updates: dict[str, Any],
) -> ReportResponse:
    """PATCH /networks/{network}/reports/{id}"""
    response = await client.patch(
        f"/networks/{network_code}/reports/{report_id}",
        json=updates,
    )
    return ReportResponse.from_gam_response(response)
```

```python
# endpoints/delete.py
"""Delete report endpoint."""

from core.client import GAMClient


async def delete_report(
    client: GAMClient,
    network_code: str,
    report_id: str,
) -> None:
    """DELETE /networks/{network}/reports/{id}"""
    await client.delete(f"/networks/{network_code}/reports/{report_id}")
```

```python
# endpoints/fetch.py
"""Fetch report rows endpoint."""

from typing import Any
from core.client import GAMClient
from models.reports import FetchRowsResponse


async def fetch_rows(
    client: GAMClient,
    network_code: str,
    report_id: str,
    page_size: int = 1000,
    page_token: str | None = None,
) -> FetchRowsResponse:
    """POST /networks/{network}/reports/{id}/results:fetchRows"""
    request_body: dict[str, Any] = {"pageSize": page_size}
    if page_token:
        request_body["pageToken"] = page_token

    response = await client.post(
        f"/networks/{network_code}/reports/{report_id}/results:fetchRows",
        json=request_body,
    )
    return FetchRowsResponse(
        rows=response.get("rows", []),
        next_page_token=response.get("nextPageToken"),
        total_row_count=response.get("totalRowCount", 0),
    )
```

```python
# endpoints/operations.py
"""Operations endpoint for async status tracking."""

import asyncio
from typing import Any
from core.client import GAMClient


async def get_operation(
    client: GAMClient,
    operation_name: str,
) -> dict[str, Any]:
    """GET /networks/{network}/operations/{id}"""
    # operation_name is full path: networks/123/operations/reports/runs/456
    return await client.get(f"/{operation_name}")


async def wait_for_operation(
    client: GAMClient,
    operation_name: str,
    timeout: int = 300,
    poll_interval: int = 5,
) -> dict[str, Any]:
    """Poll operation until complete or timeout."""
    elapsed = 0
    while elapsed < timeout:
        result = await get_operation(client, operation_name)
        if result.get("done", False):
            return result
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
    raise TimeoutError(f"Operation {operation_name} timed out after {timeout}s")
```

**Step 2: Update endpoints/__init__.py**

```python
# endpoints/__init__.py
from .create import create_report
from .run import run_report
from .get import get_report
from .list import list_reports
from .update import update_report
from .delete import delete_report
from .fetch import fetch_rows
from .operations import get_operation, wait_for_operation

__all__ = [
    "create_report",
    "run_report",
    "get_report",
    "list_reports",
    "update_report",
    "delete_report",
    "fetch_rows",
    "get_operation",
    "wait_for_operation",
]
```

**Step 3: Run all tests**

Run: `cd applications/gam-reports-mcp && uv run pytest -v`
Expected: All tests pass

**Step 4: Commit**

```bash
git add applications/gam-reports-mcp/endpoints/
git commit -m "feat(gam-reports-mcp): add all report endpoints"
```

---

## Task 14: Search Function

**Files:**
- Create: `applications/gam-reports-mcp/search.py`
- Create: `applications/gam-reports-mcp/tests/test_search.py`

**Step 1: Write failing test**

```python
# tests/test_search.py
import pytest
from search import search, matches_query


def test_matches_query_by_name():
    from models.dimensions import Dimension, DimensionCategory
    dim = Dimension(
        name="DATE",
        category=DimensionCategory.TIME,
        description="Daily granularity",
        use_case="Daily trends",
        compatible_with=[],
    )
    assert matches_query("date", dim) is True
    assert matches_query("xyz", dim) is False


def test_matches_query_by_description():
    from models.dimensions import Dimension, DimensionCategory
    dim = Dimension(
        name="DATE",
        category=DimensionCategory.TIME,
        description="Daily granularity",
        use_case="Daily trends",
        compatible_with=[],
    )
    assert matches_query("granularity", dim) is True


def test_search_finds_dimensions():
    results = search("date", search_in=["dimensions"])
    assert results["total_matches"] > 0
    assert any(m["type"] == "dimension" for m in results["matches"])


def test_search_finds_metrics():
    results = search("impressions", search_in=["metrics"])
    assert results["total_matches"] > 0
    assert any(m["type"] == "metric" for m in results["matches"])


def test_search_finds_templates():
    results = search("delivery", search_in=["templates"])
    assert results["total_matches"] > 0


def test_search_finds_strategies():
    results = search("programmatic", search_in=["strategies"])
    assert results["total_matches"] > 0


def test_search_all_categories():
    results = search("date")
    assert results["query"] == "date"
    assert "matches" in results
```

**Step 2: Run test to verify it fails**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_search.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# search.py
"""Search across knowledge base."""

from typing import Any
from pydantic import BaseModel

from models.dimensions import ALLOWED_DIMENSIONS
from models.metrics import ALLOWED_METRICS
from models.knowledge import (
    KNOWN_DOMAINS,
    KNOWN_APPS,
    AD_STRATEGIES,
    REPORT_TEMPLATES,
)


def matches_query(query: str, obj: BaseModel) -> bool:
    """Check if query matches any searchable field in the model."""
    query_lower = query.lower()
    searchable = [
        getattr(obj, "name", ""),
        getattr(obj, "description", ""),
        getattr(obj, "use_case", ""),
    ]
    return any(query_lower in str(field).lower() for field in searchable if field)


def search(
    query: str,
    search_in: list[str] | None = None,
) -> dict[str, Any]:
    """
    Search across dimensions, metrics, templates, and domain knowledge.

    Args:
        query: Search term
        search_in: Categories to search. Options: dimensions, metrics,
                   templates, domains, apps, strategies. Default: all.

    Returns:
        Dict with query, matches list, and total_matches count.
    """
    results: dict[str, Any] = {
        "query": query,
        "matches": [],
    }

    categories = search_in or [
        "dimensions",
        "metrics",
        "templates",
        "domains",
        "apps",
        "strategies",
    ]

    if "dimensions" in categories:
        for key, dim in ALLOWED_DIMENSIONS.items():
            if matches_query(query, dim):
                results["matches"].append({
                    "type": "dimension",
                    "name": key,
                    "category": dim.category.value,
                    "description": dim.description,
                    "use_case": dim.use_case,
                    "compatible_with": dim.compatible_with,
                })

    if "metrics" in categories:
        for key, metric in ALLOWED_METRICS.items():
            if matches_query(query, metric):
                results["matches"].append({
                    "type": "metric",
                    "name": key,
                    "category": metric.category.value,
                    "description": metric.description,
                    "use_case": metric.use_case,
                })

    if "templates" in categories:
        for template in REPORT_TEMPLATES:
            if matches_query(query, template):
                results["matches"].append({
                    "type": "template",
                    "name": template.name,
                    "description": template.description,
                    "dimensions": template.dimensions,
                    "metrics": template.metrics,
                })

    if "domains" in categories:
        for domain in KNOWN_DOMAINS:
            if query.lower() in domain.name.lower():
                results["matches"].append({
                    "type": "domain",
                    "name": domain.name,
                    "ad_units": domain.ad_units,
                })

    if "apps" in categories:
        for app in KNOWN_APPS:
            if query.lower() in app.name.lower():
                results["matches"].append({
                    "type": "app",
                    "name": app.name,
                    "bundle_id": app.bundle_id,
                })

    if "strategies" in categories:
        for strategy in AD_STRATEGIES:
            if matches_query(query, strategy):
                results["matches"].append({
                    "type": "strategy",
                    "name": strategy.name,
                    "description": strategy.description,
                    "typical_dimensions": strategy.typical_dimensions,
                    "typical_metrics": strategy.typical_metrics,
                })

    results["total_matches"] = len(results["matches"])
    return results
```

**Step 4: Run test to verify it passes**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_search.py -v`
Expected: PASS (7 tests)

**Step 5: Commit**

```bash
git add applications/gam-reports-mcp/search.py applications/gam-reports-mcp/tests/test_search.py
git commit -m "feat(gam-reports-mcp): add search function for knowledge base"
```

---

## Task 15: MCP Server with All Tools

**Files:**
- Create: `applications/gam-reports-mcp/server.py`
- Create: `applications/gam-reports-mcp/tests/test_server.py`

**Step 1: Write failing test**

```python
# tests/test_server.py
import pytest


def test_server_has_required_tools():
    from server import mcp

    tool_names = [tool.name for tool in mcp._tool_manager._tools.values()]

    assert "search" in tool_names
    assert "create_report" in tool_names
    assert "run_and_fetch_report" in tool_names
    assert "get_available_options" in tool_names
    assert "list_saved_reports" in tool_names
    assert "update_report" in tool_names
    assert "delete_report" in tool_names


def test_server_name():
    from server import mcp
    assert mcp.name == "gam-reports"
```

**Step 2: Run test to verify it fails**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_server.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# server.py
"""GAM Reports MCP Server - 7 goal-oriented tools for report management."""

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastmcp import FastMCP

from config.settings import settings
from core.auth import GAMAuth
from core.client import GAMClient
from models.dimensions import ALLOWED_DIMENSIONS
from models.metrics import ALLOWED_METRICS
from models.knowledge import REPORT_TEMPLATES
from models.reports import CreateReportRequest
from endpoints import (
    create_report as create_report_endpoint,
    run_report as run_report_endpoint,
    list_reports as list_reports_endpoint,
    update_report as update_report_endpoint,
    delete_report as delete_report_endpoint,
    fetch_rows,
    wait_for_operation,
)
from search import search as search_knowledge

logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastMCP):
    """Initialize GAM client on startup."""
    auth = GAMAuth(settings.credentials_path)
    async with GAMClient(auth) as client:
        app.state.client = client
        app.state.network_code = auth.network_code
        logger.info(f"GAM Reports MCP started for network {auth.network_code}")
        yield


mcp = FastMCP("gam-reports", lifespan=lifespan)


@mcp.tool()
async def search(
    query: str,
    search_in: list[str] | None = None,
) -> dict[str, Any]:
    """
    Search across dimensions, metrics, templates, and domain knowledge.

    Use this to find relevant options when you're not sure what's available.
    Searches names, descriptions, use cases, and compatibility info.

    Args:
        query: Search term (e.g., "revenue", "fill rate", "mobile app")
        search_in: Limit search to specific categories.
                   Options: dimensions, metrics, templates, domains, apps, strategies
                   Default: search all
    """
    return search_knowledge(query, search_in)


@mcp.tool()
async def create_report(
    dimensions: list[str],
    metrics: list[str],
    start_date: str,
    end_date: str,
    filters: dict[str, Any] | None = None,
    report_name: str | None = None,
) -> dict[str, Any]:
    """
    Create a new GAM report with specified dimensions and metrics.

    Use this when you need to build a custom report. Dimensions and metrics
    are validated against the curated allowlist for this network.

    Args:
        dimensions: List of dimension names (e.g., ["DATE", "AD_UNIT_NAME"])
        metrics: List of metric names (e.g., ["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"])
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        filters: Optional filters to apply
        report_name: Optional display name for the report
    """
    request = CreateReportRequest(
        display_name=report_name,
        dimensions=dimensions,
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
        filters=filters,
    )
    result = await create_report_endpoint(
        mcp.state.client,
        mcp.state.network_code,
        request,
    )
    return result.model_dump()


@mcp.tool()
async def run_and_fetch_report(
    report_id: str,
    max_rows: int = 1000,
) -> dict[str, Any]:
    """
    Execute a report and return the data rows.

    Use this when you have a report ID and want to get the actual data.
    Handles the run → poll → fetch workflow automatically.

    Args:
        report_id: The report ID to execute
        max_rows: Maximum number of rows to return (default 1000)
    """
    # Run the report
    operation_name = await run_report_endpoint(
        mcp.state.client,
        mcp.state.network_code,
        report_id,
    )

    # Wait for completion
    await wait_for_operation(mcp.state.client, operation_name)

    # Fetch results
    rows_response = await fetch_rows(
        mcp.state.client,
        mcp.state.network_code,
        report_id,
        page_size=max_rows,
    )
    return rows_response.model_dump()


@mcp.tool()
async def get_available_options() -> dict[str, Any]:
    """
    Get all available dimensions, metrics, and report templates.

    Use this first to understand what options are available for building reports.
    """
    return {
        "dimensions": {k: v.model_dump() for k, v in ALLOWED_DIMENSIONS.items()},
        "metrics": {k: v.model_dump() for k, v in ALLOWED_METRICS.items()},
        "templates": [t.model_dump() for t in REPORT_TEMPLATES],
    }


@mcp.tool()
async def list_saved_reports(
    filter_by_tag: str | None = None,
    page_size: int = 100,
) -> dict[str, Any]:
    """
    List all saved reports, optionally filtered by tag.

    Use this to see what reports already exist before creating new ones.

    Args:
        filter_by_tag: Optional tag to filter by
        page_size: Number of reports to return (default 100)
    """
    result = await list_reports_endpoint(
        mcp.state.client,
        mcp.state.network_code,
        page_size=page_size,
    )
    # TODO: Add tag filtering when GAM API supports it
    return result


@mcp.tool()
async def update_report(
    report_id: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    """
    Update an existing report configuration.

    Use this to modify dimensions, metrics, filters, or name of a saved report.

    Args:
        report_id: The report ID to update
        updates: Dictionary of fields to update
    """
    result = await update_report_endpoint(
        mcp.state.client,
        mcp.state.network_code,
        report_id,
        updates,
    )
    return result.model_dump()


@mcp.tool()
async def delete_report(report_id: str) -> dict[str, Any]:
    """
    Delete a saved report.

    Use this to remove reports that are no longer needed.

    Args:
        report_id: The report ID to delete
    """
    await delete_report_endpoint(
        mcp.state.client,
        mcp.state.network_code,
        report_id,
    )
    return {"status": "deleted", "report_id": report_id}


if __name__ == "__main__":
    import asyncio

    if settings.mcp_transport == "http":
        mcp.run(transport="http", port=settings.mcp_port)
    else:
        mcp.run(transport="stdio")
```

**Step 4: Run test to verify it passes**

Run: `cd applications/gam-reports-mcp && uv run pytest tests/test_server.py -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add applications/gam-reports-mcp/server.py applications/gam-reports-mcp/tests/
git commit -m "feat(gam-reports-mcp): add FastMCP server with 7 goal-oriented tools"
```

---

## Task 16: Dockerfile and Deployment

**Files:**
- Create: `applications/gam-reports-mcp/Dockerfile`
- Create: `applications/gam-reports-mcp/deploy.sh`

**Step 1: Create Dockerfile**

```dockerfile
# Dockerfile
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY config/ ./config/
COPY core/ ./core/
COPY endpoints/ ./endpoints/
COPY models/ ./models/
COPY search.py ./
COPY server.py ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Set PATH to include virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Reset entrypoint to run CMD directly
ENTRYPOINT []
CMD ["python", "server.py"]
```

**Step 2: Create deploy.sh**

```bash
#!/bin/bash
# deploy.sh - Deploy to Cloud Run

set -e

PROJECT_ID="${PROJECT_ID:-your-project-id}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="gam-reports-mcp"

echo "Building and deploying ${SERVICE_NAME}..."

gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --memory 512Mi \
  --max-instances 5 \
  --concurrency 80 \
  --set-secrets "/home/nonroot/.googleads.yaml=google-ads-yaml:latest" \
  --set-env-vars "MCP_TRANSPORT=http,MCP_AUTH_ENABLED=true,LOG_LEVEL=INFO"

echo "Deployment complete!"
echo "Service URL: $(gcloud run services describe ${SERVICE_NAME} --project ${PROJECT_ID} --region ${REGION} --format 'value(status.url)')"
```

**Step 3: Make deploy.sh executable and commit**

```bash
chmod +x applications/gam-reports-mcp/deploy.sh
git add applications/gam-reports-mcp/Dockerfile applications/gam-reports-mcp/deploy.sh
git commit -m "feat(gam-reports-mcp): add Dockerfile and Cloud Run deployment script"
```

---

## Task 17: Run All Tests and Final Verification

**Step 1: Run complete test suite**

Run: `cd applications/gam-reports-mcp && uv run pytest -v --cov=. --cov-report=term-missing`
Expected: All tests pass with good coverage

**Step 2: Verify server starts locally**

Run: `cd applications/gam-reports-mcp && uv run python -c "from server import mcp; print(f'Server {mcp.name} has {len(mcp._tool_manager._tools)} tools')"`
Expected: Output shows "Server gam-reports has 7 tools"

**Step 3: Final commit**

```bash
git add -A
git commit -m "feat(gam-reports-mcp): complete standalone MCP server for GAM reports

- 7 goal-oriented tools: search, create_report, run_and_fetch_report,
  get_available_options, list_saved_reports, update_report, delete_report
- Pydantic knowledge base: dimensions, metrics, filters, domain context
- One file per GAM REST endpoint with validation
- Standalone auth and async client (no imports from existing packages)
- Cloud Run deployment ready with JWT auth support"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Project scaffolding | pyproject.toml, directories |
| 2 | Error models | models/errors.py |
| 3 | Dimension models | models/dimensions.py |
| 4 | Metric models | models/metrics.py |
| 5 | Filter models | models/filters.py |
| 6 | Knowledge models | models/knowledge.py |
| 7 | Report models | models/reports.py |
| 8 | Auth module | core/auth.py |
| 9 | Client module | core/client.py |
| 10 | Settings module | config/settings.py |
| 11 | Create endpoint | endpoints/create.py |
| 12 | Run endpoint | endpoints/run.py |
| 13 | Remaining endpoints | endpoints/*.py |
| 14 | Search function | search.py |
| 15 | MCP server | server.py |
| 16 | Deployment | Dockerfile, deploy.sh |
| 17 | Final verification | Tests, verification |

**Total: 17 tasks, ~40 commits, TDD throughout**

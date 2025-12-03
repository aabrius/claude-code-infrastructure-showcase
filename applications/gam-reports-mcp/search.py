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
                    "data_format": metric.data_format.value,
                    "report_types": [rt.value for rt in metric.report_types],
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

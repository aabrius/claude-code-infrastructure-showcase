"""Tests for search functionality."""

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
    results = search("arbitrage", search_in=["templates"])
    assert results["total_matches"] > 0


def test_search_finds_strategies():
    results = search("arbitrage", search_in=["strategies"])
    assert results["total_matches"] > 0


def test_search_all_categories():
    results = search("date")
    assert results["query"] == "date"
    assert "matches" in results

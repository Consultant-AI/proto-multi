"""
Marketplace Search Engine.

Handles searching across multiple registries.
"""

from dataclasses import dataclass, field
from typing import Any

from .types import (
    PackageInfo,
    PackageType,
    SearchResult,
)


@dataclass
class SearchFilter:
    """Filters for marketplace search."""

    # Filter by type
    type: PackageType | None = None

    # Filter by author
    author: str | None = None

    # Filter by keywords
    keywords: list[str] = field(default_factory=list)

    # Only verified packages
    verified_only: bool = False

    # Exclude deprecated
    exclude_deprecated: bool = True

    # Minimum downloads
    min_downloads: int = 0

    # Minimum stars
    min_stars: int = 0

    # Sort by
    sort_by: str = "relevance"  # relevance, downloads, stars, updated

    # Sort order
    sort_order: str = "desc"  # asc, desc

    def to_query_params(self) -> dict[str, Any]:
        """Convert to API query parameters."""
        params = {}

        if self.type:
            params["type"] = self.type.value
        if self.author:
            params["author"] = self.author
        if self.keywords:
            params["keywords"] = ",".join(self.keywords)
        if self.verified_only:
            params["verified"] = "true"
        if self.exclude_deprecated:
            params["deprecated"] = "false"
        if self.min_downloads > 0:
            params["min_downloads"] = self.min_downloads
        if self.min_stars > 0:
            params["min_stars"] = self.min_stars

        params["sort"] = self.sort_by
        params["order"] = self.sort_order

        return params


class SearchEngine:
    """
    Search engine for marketplace packages.

    Features:
    - Full-text search
    - Filtering by type, author, keywords
    - Sorting and pagination
    - Local cache for faster repeat searches
    """

    def __init__(self):
        self._cache: dict[str, SearchResult] = {}
        self._cache_ttl = 300  # 5 minutes

    def search_local(
        self,
        packages: list[PackageInfo],
        query: str,
        filters: SearchFilter | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> SearchResult:
        """
        Search through a local list of packages.

        Args:
            packages: List of packages to search
            query: Search query
            filters: Optional filters
            page: Page number
            page_size: Results per page

        Returns:
            Search result
        """
        import time
        start_time = time.time()

        # Apply filters
        results = self._filter_packages(packages, filters)

        # Search
        if query:
            results = self._text_search(results, query)

        # Sort
        results = self._sort_packages(results, filters)

        # Calculate total
        total = len(results)

        # Paginate
        start = (page - 1) * page_size
        end = start + page_size
        results = results[start:end]

        duration_ms = (time.time() - start_time) * 1000

        return SearchResult(
            query=query,
            total=total,
            packages=results,
            page=page,
            page_size=page_size,
            duration_ms=duration_ms,
        )

    def _filter_packages(
        self,
        packages: list[PackageInfo],
        filters: SearchFilter | None,
    ) -> list[PackageInfo]:
        """Apply filters to packages."""
        if not filters:
            return packages

        results = packages

        if filters.type:
            results = [p for p in results if p.type == filters.type]

        if filters.author:
            results = [p for p in results if filters.author.lower() in p.author.lower()]

        if filters.keywords:
            results = [
                p for p in results
                if any(kw.lower() in [k.lower() for k in p.keywords] for kw in filters.keywords)
            ]

        if filters.verified_only:
            results = [p for p in results if p.verified]

        if filters.exclude_deprecated:
            results = [p for p in results if not p.deprecated]

        if filters.min_downloads > 0:
            results = [p for p in results if p.downloads >= filters.min_downloads]

        if filters.min_stars > 0:
            results = [p for p in results if p.stars >= filters.min_stars]

        return results

    def _text_search(
        self,
        packages: list[PackageInfo],
        query: str,
    ) -> list[PackageInfo]:
        """Full-text search across package fields."""
        query_lower = query.lower()
        query_terms = query_lower.split()

        scored = []
        for package in packages:
            score = self._calculate_relevance(package, query_terms)
            if score > 0:
                scored.append((package, score))

        # Sort by relevance
        scored.sort(key=lambda x: x[1], reverse=True)

        return [p for p, _ in scored]

    def _calculate_relevance(
        self,
        package: PackageInfo,
        query_terms: list[str],
    ) -> float:
        """Calculate relevance score for a package."""
        score = 0.0

        searchable = f"""
            {package.id}
            {package.name}
            {package.description}
            {package.author}
            {' '.join(package.keywords)}
        """.lower()

        for term in query_terms:
            # Exact match in ID or name (highest weight)
            if term in package.id.lower():
                score += 10.0
            if term in package.name.lower():
                score += 8.0

            # Match in keywords
            if any(term in kw.lower() for kw in package.keywords):
                score += 5.0

            # Match in description
            if term in package.description.lower():
                score += 2.0

            # General match
            if term in searchable:
                score += 1.0

        # Boost verified packages
        if package.verified:
            score *= 1.2

        # Slight boost for popular packages
        score += min(package.downloads / 10000, 1.0)
        score += min(package.stars / 100, 0.5)

        return score

    def _sort_packages(
        self,
        packages: list[PackageInfo],
        filters: SearchFilter | None,
    ) -> list[PackageInfo]:
        """Sort packages by specified criteria."""
        if not filters:
            return packages

        reverse = filters.sort_order == "desc"

        if filters.sort_by == "downloads":
            return sorted(packages, key=lambda p: p.downloads, reverse=reverse)
        elif filters.sort_by == "stars":
            return sorted(packages, key=lambda p: p.stars, reverse=reverse)
        elif filters.sort_by == "updated":
            return sorted(packages, key=lambda p: p.updated_at, reverse=reverse)
        elif filters.sort_by == "name":
            return sorted(packages, key=lambda p: p.name.lower(), reverse=reverse)
        else:
            # relevance - already sorted by search
            return packages

    def clear_cache(self) -> None:
        """Clear the search cache."""
        self._cache.clear()

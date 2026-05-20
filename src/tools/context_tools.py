"""
ExecutionContext tools and registry for player access.
"""

from typing import Any, Dict, Optional

from langchain_core.tools import tool

_context_registry: Dict[str, Any] = {}


def register_context(key: str, context: Any) -> str:
    _context_registry[key] = context
    return key


def get_context(key: str) -> Any:
    if key not in _context_registry:
        raise KeyError(f"ExecutionContext '{key}' not found")
    return _context_registry[key]


def clear_registry() -> None:
    _context_registry.clear()


@tool
def get_context_overview(context_key: str) -> Dict[str, Any]:
    """Return high-level context overview including resources and type."""
    ctx = get_context(context_key)
    return ctx.to_dict()


@tool
def list_resources(context_key: str) -> Dict[str, Any]:
    """List resource names in the current context."""
    ctx = get_context(context_key)
    return {"resources": ctx.resources, "count": len(ctx.resources)}


@tool
def get_resource_info(context_key: str, resource: str) -> Dict[str, Any]:
    """Return metadata for one resource."""
    ctx = get_context(context_key)
    return ctx.get_resource_info(resource).to_dict()


@tool
def get_context_schema(context_key: str) -> Dict[str, Any]:
    """Return context schema including resources and relationships."""
    ctx = get_context(context_key)
    return ctx.get_schema()


@tool
def get_item_count(context_key: str, resource: str) -> Dict[str, Any]:
    """Return row/item count for a resource."""
    ctx = get_context(context_key)
    info = ctx.get_resource_info(resource)
    return {"resource": resource, "item_count": info.item_count}


@tool
def get_field_names(context_key: str, resource: str) -> Dict[str, Any]:
    """Return field/column names for a resource."""
    ctx = get_context(context_key)
    info = ctx.get_resource_info(resource)
    return {"resource": resource, "fields": info.field_names}


@tool
def get_field_types(context_key: str, resource: str) -> Dict[str, Any]:
    """Return field/column data types for a resource."""
    ctx = get_context(context_key)
    info = ctx.get_resource_info(resource)
    return {
        "resource": resource,
        "field_types": {field.name: field.dtype for field in info.fields},
    }


@tool
def get_sample_items(context_key: str, resource: str, limit: int = 5) -> Dict[str, Any]:
    """Return sample rows from a resource."""
    ctx = get_context(context_key)
    df = ctx.read_resource(resource, limit=limit)
    return {"resource": resource, "sample": df.to_dict(orient="records")}


@tool
def get_field_statistics(context_key: str, resource: str) -> Dict[str, Any]:
    """Return numeric summary statistics for a resource."""
    ctx = get_context(context_key)
    df = ctx.read_resource(resource)
    describe = df.describe(include="all").transpose().fillna("").to_dict(orient="index")
    return {"resource": resource, "statistics": describe}


@tool
def get_missing_values(context_key: str, resource: str) -> Dict[str, Any]:
    """Return missing-value counts by field for a resource."""
    ctx = get_context(context_key)
    df = ctx.read_resource(resource)
    missing = {col: int(val) for col, val in df.isna().sum().to_dict().items()}
    return {"resource": resource, "missing_values": missing}


@tool
def get_unique_values(
    context_key: str, resource: str, field: str, limit: Optional[int] = 20
) -> Dict[str, Any]:
    """Return distinct values for a field within a resource."""
    ctx = get_context(context_key)
    values = ctx.get_field_values(resource=resource, field=field, limit=limit)
    return {"resource": resource, "field": field, "values": values}


@tool
def get_relationships(context_key: str) -> Dict[str, Any]:
    """Return discovered relationships across resources."""
    ctx = get_context(context_key)
    return {"relationships": [rel.to_dict() for rel in ctx.get_relationships()]}

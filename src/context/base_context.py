"""
ExecutionContext base classes and models.

This module defines the generic abstraction for the environment in which
agents operate. A context may represent a codebase, directory tree, API,
website, terminal workspace, operating system surface, or any other resource
collection a project wants to expose.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional


class ContextType(str, Enum):
    """Enumeration of supported execution context types."""

    DATABASE = "database"
    DIRECTORY = "directory"
    API = "api"
    WEBSITE = "website"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class ResourceInfo:
    """Information about a single resource in the execution context."""

    name: str
    location: Optional[str] = None
    size_in_bytes: Optional[int] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "location": self.location,
            "size_in_bytes": self.size_in_bytes,
            "description": self.description,
            "resource_type": self.resource_type,
            "metadata": self.metadata,
        }


class ExecutionContext(ABC):
    """
    Abstract base class for all execution contexts.
    Provides a unified interface for accessing the operational environment.
    """

    def __init__(self, name: str = "context", description: Optional[str] = None):
        self._name = name
        self._description = description
        self._resource_cache: Dict[str, ResourceInfo] = {}

    @property
    @abstractmethod
    def context_type(self) -> ContextType:
        """Return the type of this context."""
        pass

    @property
    @abstractmethod
    def resources(self) -> List[str]:
        """Return list of resource names in this context."""
        pass

    @abstractmethod
    def _load_resource_info(self, resource: str) -> ResourceInfo:
        """Load metadata for a specific resource."""
        pass

    @abstractmethod
    def read_resource(self, resource: str, **kwargs) -> Any:
        """Read a resource and return a context-specific representation."""
        pass

    @abstractmethod
    def iter_resource(self, resource: str, **kwargs) -> Iterator[Any]:
        """Iterate over items from a resource using a context-specific strategy."""
        pass

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def is_multi_resource(self) -> bool:
        return len(self.resources) > 1

    @property
    def primary_resource(self) -> Optional[str]:
        return self.resources[0] if self.resources else None

    def get_resource_info(self, resource: str) -> ResourceInfo:
        if resource not in self.resources:
            raise ValueError(
                f"Resource '{resource}' not found. Available: {self.resources}"
            )

        if resource not in self._resource_cache:
            self._resource_cache[resource] = self._load_resource_info(resource)

        return self._resource_cache[resource]

    def get_all_resource_info(self) -> Dict[str, ResourceInfo]:
        return {
            resource: self.get_resource_info(resource) for resource in self.resources
        }

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "context_type": self.context_type.value,
            "is_multi_resource": self.is_multi_resource,
            "resources": {
                name: info.to_dict()
                for name, info in self.get_all_resource_info().items()
            },
        }

    def validate(self) -> bool:
        if not self.resources:
            raise ValueError("Context has no resources")

        for resource in self.resources:
            self.get_resource_info(resource)

        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "context_type": self.context_type.value,
            "resources": self.resources,
            "is_multi_resource": self.is_multi_resource,
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"resources={self.resources}, "
            f"context_type='{self.context_type.value}')"
        )

    def __str__(self) -> str:
        resource_info = (
            f"{len(self.resources)} resource(s)"
            if self.is_multi_resource
            else self.resources[0]
        )
        return f"{self.name} ({self.context_type.value}: {resource_info})"

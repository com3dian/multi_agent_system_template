"""
ContextFactory - Minimal entry point for creating execution contexts.

This template keeps the factory intentionally small so it can support many
different context types without hardcoding file formats or dataset-specific
logic into the base layer.

The only built-in behavior is:
- return an existing `ExecutionContext` unchanged
- reject unsupported inputs with a clear error

Extension ideas that template users can implement in their own projects:

    # Example: explicit kind-based registration
    # ContextFactory.register("directory", DirectoryContext.from_directory)
    # ctx = ContextFactory.create("directory", path="/repo")

    # Example: directory helper on a custom context
    # class DirectoryContext(ExecutionContext):
    #     @classmethod
    #     def from_directory(cls, path: str) -> "DirectoryContext":
    #         ...

    # Example: path-based auto-detection in a project-specific factory
    # @classmethod
    # def create_from_path(cls, path: str, **kwargs) -> ExecutionContext:
    #     if os.path.isdir(path):
    #         return DirectoryContext.from_directory(path, **kwargs)
    #     raise ValueError(f"Unsupported context source: {path}")
"""

from typing import Any

from .base_context import ExecutionContext


class ContextFactory:
    """Minimal factory for `ExecutionContext` instances."""

    @classmethod
    def create(cls, source: Any, **_: Any) -> ExecutionContext:
        """
        Create an execution context from a supported source.

        Currently supported:
        - an existing `ExecutionContext` instance
        """
        if isinstance(source, ExecutionContext):
            return source

        raise ValueError(
            "Unsupported context source. Pass an existing ExecutionContext "
            "or extend ContextFactory for project-specific creation logic."
        )


def create_context(source: Any, **kwargs: Any) -> ExecutionContext:
    """Convenience wrapper around `ContextFactory.create()`."""
    return ContextFactory.create(source, **kwargs)

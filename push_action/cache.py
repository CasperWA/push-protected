"""push_action.cache

A simple implementation of an in-memory cache.
It's a glorified dictionary and is mainly here as a representation of playing around
with and learning dunder methods.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Iterator


class InMemoryCache:
    """In-memory key-value cache"""

    def __len__(self):
        """Number of cached keys"""
        return len(self.__dict__)

    def __getitem__(self, key: str) -> "Any":
        """Get cached value, example: `self[key]`"""
        if not isinstance(key, str):
            raise TypeError("Supplied key must be a string.")
        if key not in self.__dict__:
            raise KeyError(f"{key!r} not found in cache.")
        return self.__dict__[key]

    def __setitem__(self, key: str, value: "Any") -> None:
        """Set cached value, example: `self[key] = value`"""
        if not isinstance(key, str):
            raise TypeError("Supplied key must be a string.")
        self.__dict__[key] = value

    def __delitem__(self, key: str) -> None:
        """Delete cached value, example: `del self[key]`"""
        if not isinstance(key, str):
            raise TypeError("Supplied key must be a string.")
        if key not in self.__dict__:
            raise KeyError(f"{key!r} not found in cache.")
        del self.__dict__[key]

    def __iter__(self) -> "Iterator":
        """Iterate over the cached keys"""
        return iter(self.__dict__.keys())

    def __contains__(self, item: str) -> bool:
        """Whether item is cached or not"""
        if not isinstance(item, str):
            raise TypeError("Item must be a string.")
        return item in self.__dict__

    def get(self, key: str, fallback: "Any" = None) -> "Any":
        """Get cached value from key"""
        return self.__dict__.get(key, fallback)


IN_MEMORY_CACHE = InMemoryCache()

from typing import Any, Iterator, Union


class InMemoryCache:
    """In-memory key-value cache"""

    def __len__(self):
        """Number of cached keys"""
        return len(self.__dict__)

    def __getitem__(self, key: Union[str, int]) -> Any:
        """Get cached value, example: `self[key]`"""
        if not isinstance(key, (str, int)):
            raise TypeError("Supplied key must be a string or integer.")
        if key not in self.__dict__:
            raise KeyError(f"{key!r} not found in cache.")
        return self.__dict__[key]

    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """Set cached value, example: `self[key] = value`"""
        if not isinstance(key, (str, int)):
            raise TypeError("Supplied key must be a string or integer.")
        self.__dict__[key] = value

    def __delitem__(self, key: Union[str, int]) -> None:
        """Delete cached value, example: `del self[key]`"""
        if not isinstance(key, (str, int)):
            raise TypeError("Supplied key must be a string or integer.")
        if key not in self.__dict__:
            raise KeyError(f"{key!r} not found in cache.")
        del self.__dict__[key]

    def __iter__(self) -> Iterator:
        """Iterate over the cached keys"""
        return iter(self.__dict__.keys())

    def __contains__(self, item: Union[str, int]) -> bool:
        """Whether item is cached or not"""
        if not isinstance(item, (str, int)):
            raise TypeError("Item must be a string or integer.")
        return item in self.__dict__.keys()

    def get(self, key: Union[str, int], fallback: Any = None) -> Any:
        """Get cached value from key"""
        return self.__dict__.get(key, fallback)


IN_MEMORY_CACHE = InMemoryCache()

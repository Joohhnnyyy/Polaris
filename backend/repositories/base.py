from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def find(self, id: str) -> Optional[T]:
        raise NotImplementedError
        
    def save(self, entity: T) -> T:
        raise NotImplementedError
        
    def update(self, entity: T) -> T:
        raise NotImplementedError
        
    def delete(self, id: str) -> bool:
        raise NotImplementedError

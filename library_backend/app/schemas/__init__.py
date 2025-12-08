"""Pydantic схемы"""

from .auth import TelegramAuthData, TokenResponse, UserInfo, SubscriptionStatus
from .library import (
    Category, CategoryCreate, CategoryUpdate,
    Tag, TagCreate,
    Material, MaterialListItem, MaterialCreate, MaterialUpdate,
    Attachment, AttachmentCreate,
    Favorite, FavoriteCreate,
    View, ViewCreate,
    MaterialFilters, PaginatedResponse
)

__all__ = [
    # Auth
    'TelegramAuthData',
    'TokenResponse',
    'UserInfo',
    'SubscriptionStatus',
    
    # Library
    'Category',
    'CategoryCreate',
    'CategoryUpdate',
    'Tag',
    'TagCreate',
    'Material',
    'MaterialListItem',
    'MaterialCreate',
    'MaterialUpdate',
    'Attachment',
    'AttachmentCreate',
    'Favorite',
    'FavoriteCreate',
    'View',
    'ViewCreate',
    'MaterialFilters',
    'PaginatedResponse',
]

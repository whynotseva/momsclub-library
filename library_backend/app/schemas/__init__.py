"""Pydantic схемы"""

from .auth import TelegramAuthData, TokenResponse, UserInfo, SubscriptionStatus, LoyaltyInfo
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
    'LoyaltyInfo',
    
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

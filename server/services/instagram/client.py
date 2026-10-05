from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .commons import InstagramMedia, InstagramUser

class InstagramClient(ABC):
  
  @abstractmethod
  def _ensure_session(self): pass
  
  @abstractmethod
  def lookup_user(self, username: str) -> InstagramUser: pass
  
  @abstractmethod
  def fetch_user_media(
    self,
    username_or_id: str,
    count: int,
    max_id: Optional[str],
  ) -> tuple[list[InstagramMedia], Optional[str]]:
    pass
  
  @abstractmethod
  def fetch_user_posts(self, username: str, posts_limit: int) -> list[dict]: pass
  
  @abstractmethod
  def close(self): pass
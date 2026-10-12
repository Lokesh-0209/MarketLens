import hashlib
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from datetime import datetime, timezone
from pydantic import BaseModel, Field, computed_field, field_validator

def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = [
        (k,v)
        for k,v in parse_qsl(parts.query,keep_blank_values=True)
        if not k.lower().startswith("utm_")
    ]
    path = parts.path.rstrip("/") or '/'
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), "")
    )

def make_article_id(url: str) -> str:
    return hashlib.sha256(normalize_url(url).encode("utf-8")).hexdigest()[:16]


class Article(BaseModel):
    title: str
    summary: str | None = None
    url: str
    source: str
    published_at: datetime
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider: str
    language: str = "en"

    @field_validator("title","url","source","provider")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v
    
    @field_validator("summary")
    @classmethod
    def blank_summary_to_none(cls, v:str | None):
        if v is None:
            return None
        v = v.strip()
        return v or None

    @field_validator("published_at","fetched_at")
    @classmethod
    def to_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("datetime must be timezone aware")
        return v.astimezone(timezone.utc)

    @computed_field
    @property
    def id(self) -> str:
        return make_article_id(self.url)

    @property
    def text(self) -> str:
        return f"{self.title}. {self.summary}" if self.summary else self.title
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from marketlens.schemas import Article


def make(**overrides):
    data = dict(
        title="Fed holds rates steady",
        url="https://example.com/news/fed-holds",
        source="Example Wire",
        published_at="2026-10-11T10:30:00+05:30",
        provider="test",
    )
    data.update(overrides)
    return Article(**data)


def test_published_at_converted_to_utc():
    a = make()
    assert a.published_at == datetime(2026, 10, 11, 5, 0, tzinfo=timezone.utc)
    assert a.published_at.utcoffset() == timedelta(0)


def test_naive_datetime_rejected():
    with pytest.raises(ValidationError):
        make(published_at=datetime(2026, 10, 11, 10, 30))


def test_blank_title_rejected():
    with pytest.raises(ValidationError):
        make(title="   ")


def test_id_ignores_tracking_case_and_trailing_slash():
    a = make(url="https://example.com/news/fed-holds")
    b = make(url="HTTPS://Example.com/news/fed-holds/?utm_source=x#top")
    assert a.id == b.id


def test_different_urls_get_different_ids():
    assert make(url="https://example.com/a").id != make(url="https://example.com/b").id


def test_text_joins_title_and_summary():
    assert make(summary="Policy unchanged.").text == "Fed holds rates steady. Policy unchanged."
    assert make().text == "Fed holds rates steady"


def test_blank_summary_becomes_none():
    assert make(summary="  ").summary is None
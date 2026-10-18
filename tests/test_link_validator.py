import pytest

from app.services.link_validator_service import LinkValidatorService

validate = LinkValidatorService.validate_telegram_post_link


@pytest.mark.parametrize(
    "raw, final",
    [
        ("https://t.me/some_channel/42", "https://t.me/some_channel/42"),
        ("t.me/some_channel/42", "https://t.me/some_channel/42"),
        ("http://www.t.me/some_channel/7?single", "https://t.me/some_channel/7"),
        ("https://t.me/c/1234567890/15", "https://t.me/c/1234567890/15"),
    ],
)
def test_valid_links_are_normalised(raw, final):
    result = validate(raw)
    assert result["is_valid"] is True
    assert result["final_link"] == final


@pytest.mark.parametrize(
    "raw",
    ["", "https://example.com/post/1", "https://t.me/some_channel", "https://t.me/ab/1", "https://t.me/some_channel/abc"],
)
def test_invalid_links_are_rejected(raw):
    result = validate(raw)
    assert result["is_valid"] is False
    assert result["error"]

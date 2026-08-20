from __future__ import annotations

from app.verification.email_verifier import verify_email
from app.verification.phone_verifier import verify_phone


def test_verify_email_valid_format_and_domain():
    result = verify_email("someone@gmail.com")
    assert result.status == "valid"
    assert result.is_valid_format is True
    assert result.has_mx_record is True


def test_verify_email_malformed_is_invalid():
    result = verify_email("not-an-email")
    assert result.status == "invalid"
    assert result.is_valid_format is False


def test_verify_email_none_is_unverifiable():
    result = verify_email(None)
    assert result.status == "unverifiable"


def test_verify_email_nonexistent_domain_is_invalid():
    result = verify_email("someone@thisdomaindefinitelydoesnotexist12345abc.com")
    assert result.status == "invalid"
    assert result.is_valid_format is True
    assert result.has_mx_record is False


def test_verify_phone_valid_us_number():
    result = verify_phone("+14155552671")
    assert result.status == "valid"
    assert result.is_valid is True
    assert result.formatted_e164 == "+14155552671"


def test_verify_phone_too_short_is_invalid():
    result = verify_phone("123")
    assert result.status == "invalid"
    assert result.is_valid is False


def test_verify_phone_none_is_not_available():
    result = verify_phone(None)
    assert result.status == "not_available"

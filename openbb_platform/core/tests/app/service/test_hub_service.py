"""Test the hub_service.py module."""
# pylint: disable=W0212
# ruff: noqa: S105 S106


from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.model.hub.features_keys import FeaturesKeys
from openbb_core.app.service.hub_service import (
    Credentials,
    HubService,
    HubSession,
    HubUserSettings,
    OpenBBError,
)
from pydantic import SecretStr


@pytest.fixture
def mocker():
    """Fixture for mocker."""
    with patch("openbb_core.app.service.hub_service.HubService") as mock:
        yield mock


def test_connect_with_email_password():
    """Test connect with email and password."""
    mock_hub_session = MagicMock(spec=HubSession)
    with patch(
        "requests.post", return_value=MagicMock(status_code=200, json=lambda: {})
    ), patch.object(
        HubService,
        "_get_session_from_email_password",
        return_value=mock_hub_session,
    ):
        hub_service = HubService()
        result = hub_service.connect(email="test@example.com", password="password")

        assert result == mock_hub_session
        assert hub_service.session == mock_hub_session


def test_connect_with_sdk_token():
    """Test connect with Platform personal access token."""
    mock_hub_session = MagicMock(spec=HubSession)
    with patch(
        "requests.post", return_value=MagicMock(status_code=200, json=lambda: {})
    ), patch.object(
        HubService, "_get_session_from_platform_token", return_value=mock_hub_session
    ):
        hub_service = HubService()
        result = hub_service.connect(pat="pat")

        assert result == mock_hub_session
        assert hub_service.session == mock_hub_session


def test_connect_without_credentials():
    """Test connect without credentials."""
    hub_service = HubService()
    with pytest.raises(
        OpenBBError, match="Please provide 'email' and 'password' or 'pat'"
    ):
        hub_service.connect()


def test_get_session_from_email_password():
    """Test get session from email and password."""

    with patch(
        "openbb_core.app.service.hub_service.post",
        return_value=MagicMock(
            status_code=200,
            json=lambda: {
                "access_token": "token",
                "token_type": "Bearer",
                "uuid": "uuid",
                "email": "email",
                "username": "username",
                "primary_usage": "primary_usage",
            },
        ),
    ):
        result = HubService()._get_session_from_email_password("email", "password")
        assert isinstance(result, HubSession)


def test_get_session_from_platform_token():
    """Test get session from Platform personal access token."""

    with patch(
        "openbb_core.app.service.hub_service.post",
        return_value=MagicMock(
            status_code=200,
            json=lambda: {
                "access_token": "token",
                "token_type": "Bearer",
                "uuid": "uuid",
                "username": "username",
                "email": "email",
                "primary_usage": "primary_usage",
            },
        ),
    ):
        mock_token = (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRiMjEyZDdhZj"
            "c2MWI0ZTNlOGNjZGM3OWQ5Zjk4YWM5In0.eyJhY2Nlc3NfdG9rZW4iOiJ0"
            "b2tlbiIsInRva2VuX3R5cGUiOiJCZWFyZXIiLCJ1dWlkIjoidXVpZCIsInV"
            "zZXJuYW1lIjoidXNlcm5hbWUiLCJlbWFpbCI6ImVtYWlsIiwicHJpbWFyeV9"
            "1c2FnZSI6InByaW1hcnlfdXNhZ2UifQ.FAtE8-a1a-313Zoa6dREIxGZOHaW9"
            "-JLZnFzyJ6dlHBZnkjQT2tfaaefxnTdAlSmToQwxGykvuatmI7L0wztPQ"
        )

        result = HubService()._get_session_from_platform_token(mock_token)
        assert isinstance(result, HubSession)


def test_disconnect():
    """Test disconnect."""

    with patch(
        "openbb_core.app.service.hub_service.get",
        return_value=MagicMock(
            status_code=200,
            json=lambda: {"success": True},
        ),
    ):
        mock_hub_session = MagicMock(
            spec=HubSession, access_token=SecretStr("token"), token_type="Bearer"
        )
        hub_service = HubService(session=mock_hub_session)

        assert hub_service.disconnect() is True
        assert hub_service.session is None


def test_get_user_settings():
    """Test get user settings."""
    with patch(
        "openbb_core.app.service.hub_service.get",
        return_value=MagicMock(
            status_code=200,
            json=lambda: {},
        ),
    ):
        mock_hub_session = MagicMock(
            spec=HubSession, access_token=SecretStr("token"), token_type="Bearer"
        )

        user_settings = HubService()._get_user_settings(mock_hub_session)
        assert isinstance(user_settings, HubUserSettings)


def test_put_user_settings():
    """Test put user settings."""

    with patch(
        "openbb_core.app.service.hub_service.put",
        return_value=MagicMock(
            status_code=200,
        ),
    ):
        mock_hub_session = MagicMock(
            spec=HubSession, access_token=SecretStr("token"), token_type="Bearer"
        )
        mock_user_settings = MagicMock(spec=HubUserSettings)

        assert (
            HubService()._put_user_settings(mock_hub_session, mock_user_settings)
            is True
        )


def test_hub2platform():
    """Test hub2platform."""
    mock_user_settings = MagicMock(spec=HubUserSettings)
    mock_user_settings.features_keys = FeaturesKeys(
        API_KEY_FINANCIALMODELINGPREP="fmp",
        API_POLYGON_KEY="polygon",
        API_FRED_KEY="fred",
    )

    credentials = HubService.hub2platform(mock_user_settings)
    assert isinstance(credentials, Credentials)
    assert credentials.fmp_api_key.get_secret_value() == "fmp"
    assert credentials.polygon_api_key.get_secret_value() == "polygon"
    assert credentials.fred_api_key.get_secret_value() == "fred"


def test_platform2hub():
    """Test platform2hub."""
    mock_credentials = MagicMock(spec=Credentials)
    mock_credentials.fmp_api_key = SecretStr("fmp")
    mock_credentials.polygon_api_key = SecretStr("polygon")
    mock_credentials.fred_api_key = SecretStr("fred")

    user_settings = HubService.platform2hub(mock_credentials)
    assert isinstance(user_settings, HubUserSettings)
    assert user_settings.features_keys.API_KEY_FINANCIALMODELINGPREP == "fmp"
    assert user_settings.features_keys.API_POLYGON_KEY == "polygon"
    assert user_settings.features_keys.API_FRED_KEY == "fred"

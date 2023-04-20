from typing import Optional
from google.oauth2.credentials import Credentials

import pytest
from pathlib import Path

from gslide2media.google.auth import AuthGoogle
from gslide2media.config import API_SCOPES
from gslide2media.options import Options


@pytest.fixture(
    params=[Path("token.json"), "/Users/davidmidlo/projects/gslide2jpeg/token.json"]
)
def token_file(request):
    return request.param

@pytest.fixture()
def default_options():
    return Options()


@pytest.fixture()
def creds_from_token_file(token_file):
    return AuthGoogle.load_google_auth_creds_from_file(token_file, API_SCOPES)


def test_load_google_auth_creds_from_file(token_file):
    creds = AuthGoogle.load_google_auth_creds_from_file(token_file, API_SCOPES)

    if token_file is None:
        assert creds is None
    else:
        assert isinstance(creds, Credentials)


def test_refresh_google_auth_creds(creds_from_token_file):
    refreshed_creds = AuthGoogle.refresh_google_auth_creds(creds_from_token_file)

    if (
        creds_from_token_file is None
        or not creds_from_token_file.valid
        or creds_from_token_file.expired
    ):
        assert refreshed_creds is None
    else:
        assert isinstance(refreshed_creds, Credentials)
        assert refreshed_creds.valid
        assert not refreshed_creds.expired

@pytest.mark.parametrize(
    "options_set, options_obj",
    [
        ("None", None),
        ("from_file", AuthGoogle.load_google_auth_creds_from_file(Path("token.json"), API_SCOPES))
    ],
)
def test_initiate_google_oauth_flow(options_set, options_obj, default_options):
    obtained_creds = AuthGoogle.initiate_google_oauth_flow(options_obj, default_options.credentials_file, API_SCOPES)

    assert isinstance(obtained_creds, Credentials)

    creds = AuthGoogle.refresh_google_auth_creds(obtained_creds)

    assert creds.valid
    assert not creds.expired

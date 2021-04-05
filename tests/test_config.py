# pylint:disable=missing-function-docstring
import pytest

from incognitus_client import IncognitusConfig


def test_config__sets_tenant_id():
    config = IncognitusConfig("abc", "def")

    assert config.tenant_id == "abc"


def test_config__sets_application_id():
    config = IncognitusConfig("abc", "def")

    assert config.application_id == "def"


def test_config__raises_when_missing_tenant_id():
    with pytest.raises(ValueError) as ex:
        IncognitusConfig("", "def")

    assert 'Tenant ID is required' in str(ex.value)


def test_config__raises_when_missing_application_id():
    with pytest.raises(ValueError) as ex:
        IncognitusConfig("abc", "")

    assert ex is not None
    assert 'Application ID is required' in str(ex.value)

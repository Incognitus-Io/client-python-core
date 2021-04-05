# pylint:disable=missing-function-docstring
import pytest
import requests

from incognitus_client import Incognitus, IncognitusConfig, NotSupportedError, IncognitusError
from incognitus_client.incognitus import DEFAULT_URL


def test_instance__raises_when_accessed_before_initialized():
    with pytest.raises(NotSupportedError):
        Incognitus.instance()


def test_is_ready__returns_false_before_initalized():
    assert Incognitus.is_ready() is False


def test_initalize__returns_the_service(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': []})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))

    assert svc is not None


def test_initalize__fetches_all_features(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': []})

    Incognitus.initialize(IncognitusConfig("abc", "def"))

    request = requests_mock.last_request

    assert request is not None
    assert request.url == '{}/feature'.format(DEFAULT_URL)


def test_is_ready__returns_true_after_initailizing(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': []})

    Incognitus.initialize(IncognitusConfig("abc", "def"))

    assert Incognitus.is_ready() is True


def test_instance__returns_the_matching_service(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': []})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))

    assert Incognitus.instance() is svc


def test_get_all_features__sends_x_headers(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': []})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))
    svc.get_all_features()

    request = requests_mock.last_request
    assert request.headers.get('X-Tenant') == 'abc'
    assert request.headers.get('X-Application') == 'def'


def test_get_all_features__throws_when_api_failure(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': []})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))

    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.not_found)  # pylint: disable=no-member

    with pytest.raises(IncognitusError):
        svc.get_all_features()


def test_get_feature__sends_x_headers(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': []})
    requests_mock.get('{}/feature/foobar'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'isEnabled': True})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))
    svc.get_feature('foobar')

    request = requests_mock.last_request
    assert request.headers.get('X-Tenant') == 'abc'
    assert request.headers.get('X-Application') == 'def'


def test_get_feature__returns_false_on_api_failure(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': []})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))

    requests_mock.get('{}/feature/foobar'.format(DEFAULT_URL),
                      status_code=requests.codes.not_found)  # pylint: disable=no-member
    feature = svc.get_feature('foobar')

    assert feature is False


def test_get_feature__returns_false_when_feature_is_off(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': []})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))

    requests_mock.get('{}/feature/foobar'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'isEnabled': False})
    feature = svc.get_feature('foobar')

    assert feature is False


def test_get_feature__returns_true_when_feature_is_on(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': []})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))

    requests_mock.get('{}/feature/foobar'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'isEnabled': True})
    feature = svc.get_feature('foobar')

    assert feature is True


def test_has_cached_feature__returns_true_when_feature_is_cached(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': [{'name': 'foobar', 'isEnabled': True}]})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))

    cached = svc.has_cached_feature('foobar')

    assert cached is True


def test_has_cached_feature__returns_false_when_feature_is_not_cached(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': [{'name': 'foobar', 'isEnabled': True}]})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))

    cached = svc.has_cached_feature('fizzbuzz')

    assert cached is False


def test_is_enabled__gets_feature_if_not_in_cache(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': []})
    requests_mock.get('{}/feature/foobar'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'isEnabled': True})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))

    results = svc.is_enabled('foobar')

    assert results is True


def test_is_enabled__returns_feature_from_cache(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': [{'name': 'foobar', 'isEnabled': True}]})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))

    results = svc.is_enabled('foobar')

    assert results is True


def test_is_disabled__gets_feature_if_not_in_cache(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': []})
    requests_mock.get('{}/feature/foobar'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'isEnabled': True})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))

    results = svc.is_disabled('foobar')

    assert results is False


def test_is_disabled__returns_feature_from_cache(requests_mock):
    requests_mock.get('{}/feature'.format(DEFAULT_URL),
                      status_code=requests.codes.ok,   # pylint: disable=no-member
                      json={'Features': [{'name': 'foobar', 'isEnabled': True}]})

    svc = Incognitus.initialize(IncognitusConfig("abc", "def"))

    results = svc.is_disabled('foobar')

    assert results is False

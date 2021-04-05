"""Incognitus python client"""

from typing import Optional, Type
import requests

DEFAULT_URL = 'https://incognitus.io/api'


class IncognitusError(Exception):
    ''' An api failure has occured. '''


class NotSupportedError(Exception):
    ''' The current state is invalid and not supported. '''


class IncognitusConfig:  # pylint: disable=too-few-public-methods
    '''
    The configuration options to initialize the Incognitus service.

    Args:
        tenant_id (str): Your tenant ID, found in the managment console.
        application_id (str): The application ID, found in the management console.
        api_url (str, optional): The api to use to check features.
    '''

    def __init__(self, tenant_id: str, application_id: str, api_url: Optional[str] = None) -> None:
        if not tenant_id or tenant_id.isspace():
            raise ValueError('Tenant ID is required')
        if not application_id or application_id.isspace():
            raise ValueError('Application ID is required')

        self.tenant_id = tenant_id
        self.application_id = application_id
        self.api_url = api_url


class Incognitus:
    '''A service for communicating with the Incognitus API.'''
    __instance = None

    def __init__(self, config: IncognitusConfig) -> None:
        self.__feature_cache = {}
        self.__headers = {
            'X-Tenant': config.tenant_id,
            'X-Application': config.application_id,
        }
        self.__api_url = config.api_url

    @staticmethod
    def instance() -> Optional[Type['Incognitus']]:
        '''
        Returns:
            Incognitus: The instance of the Incognitus service if initialized, else None.
        '''
        if not Incognitus.__instance:
            raise NotSupportedError('You must initialize the service first.')

        return Incognitus.__instance

    @staticmethod
    def is_ready() -> bool:
        '''
        Returns:
            bool: ``True`` if the service is ready for use, else ``False``.
        '''
        return Incognitus.__instance is not None

    @staticmethod
    def initialize(config: IncognitusConfig) -> Optional[Type['Incognitus']]:
        '''Initalizes the Incognitus service and fetches all features.

        Args:
            config (IncognitusConfig): Config the configuration options.

        Returns:
            Incognitus: The instance of the service initialized.
        '''
        svc = Incognitus(config)
        svc.get_all_features()
        Incognitus.__instance = svc

        return svc

    @property
    def __base_uri(self) -> str:
        base = self.__api_url
        if not base or base.isspace():
            base = DEFAULT_URL

        return '{base_uri}/feature'.format(base_uri=base)

    def is_enabled(self, name: str) -> bool:
        '''Checks if a feature flag is enabled.

        If not previously fetched, this will also fetch the flag.

        Args:
            name (str): The name of the feature flag.

        Returns:
            bool: ``True`` if the feature is enabled, else ``False``.
        '''
        if not self.has_cached_feature(name):
            return self.get_feature(name)

        return self.__feature_cache[name]

    def is_disabled(self, name: str) -> bool:
        '''Checks if a feature flag is disabled.

        If not previously fetched, this will also fetch the flag.

        Args:
            name (str): The name of the feature flag.

        Returns:
            bool: ``True`` if the feature is disabled, else ``False``.
        '''
        if not self.has_cached_feature(name):
            return not self.get_feature(name)

        return not self.__feature_cache[name]

    def has_cached_feature(self, name: str) -> bool:
        '''Checks if a feature flag has been fetched and cached.

        Args:
            name (str): The name of the feature flag.

        Raises:
            IncognitusError: An api failure has occurred.

        Returns:
            bool: ``True`` if the feature flag has been cached, else ``False``.
        '''
        return name in self.__feature_cache

    def get_all_features(self) -> None:
        ''' Fetches all feature flags for the configured service. '''
        res = requests.get(self.__base_uri, headers=self.__headers)
        if not res.ok:
            raise IncognitusError()

        data = res.json()
        self.__feature_cache = {x['name']: x['isEnabled']
                                for x in data['Features']}

    def get_feature(self, name: str) -> bool:
        '''Fetches a specified feature flag.

        Args:
            name (str): The name of the feature flag.

        Returns:
            bool: The state of the feature is disabled, else ``False`` if the request fails.
        '''
        res = requests.get(
            '{base}/{name}'.format(base=self.__base_uri, name=name),
            headers=self.__headers
        )
        if not res.ok:
            return False

        data = res.json()
        self.__feature_cache[name] = data['isEnabled']

        return self.__feature_cache[name]

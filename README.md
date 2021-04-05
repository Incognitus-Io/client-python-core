# Incognitus Feature Flag

![Continuous Integration](https://github.com/Incognitus-Io/client-python-core/workflows/Continuous%20Integration/badge.svg)
[![codecov](https://codecov.io/gh/Incognitus-Io/client-python-core/branch/master/graph/badge.svg?token=Bztt7J8tUJ)](https://codecov.io/gh/Incognitus-Io/client-python-core)
[![PyPI version](https://badge.fury.io/py/incognitus-client.svg)](https://badge.fury.io/py/incognitus-client)

## Integrating Incognitus

## Initializing the service

Before you're able to use the service you'll need to initialize with your tenant and application IDs.

#### main.py

Initialize Incognitus service

```python
from incognitus_client import Incognitus, IncognitusConfig

Incognitus.initialize(
  IncognitusConfig(
    "{your tenant key}",
    "{your app id}"
  )
)
```

| Key            | Description               |
| -------------- | ------------------------- |
| tenant_id      | Your tenant id            |
| application_id | The id of the application |

## Checking features

```python
from incognitus_client import Incognitus

svc = Incognitus.instance

response = "old feature text"
if (svc.is_enabled("{feature name}")):
  response = "new feature text"
```

## Methods

| Method                        | Description                                                 |
| ----------------------------- | ----------------------------------------------------------- |
| Incognitus.initialize(config) | Initializes the service (must be called first)              |
| Incognitus.instance()         | The shared instance of the service                          |
| svc.is_enabled(featureName)   | Checks if the flag is enabled                               |
| svc.is_disabled(featureName)  | Check if the flag is disabled                               |
| svc.get_feature(featureName)  | Fetches the feature from the server and returns it's status |
| svc.get_all_features()        | Fetches all features and stores them in the cache           |

## Caching

Currently all known feature flags are cached when the app initializes. New features that are not found
in the cache are retrieved on-demand. The cache stays in place until the app is reloaded or by calling the `get_all_features()` method on the service.

### Future Caching Stories

- Save verified cache to local storage
- Provide hard cache refresh (wipe cache if fails)
- Provide soft cache refresh (keep cache if fails)
- Customizable cache refresh times
- Option to disable cache

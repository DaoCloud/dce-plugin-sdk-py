# dce-plugin-sdk-py

DCE plugin SDK for Python.

## Requirements

- Python 2.7.*

## Installation

### Install from PYPI:

```bash
$ pip install dce-plugin-sdk
```

### Install from source:

```bash
$ pip install https://github.com/DaoCloud/dce-plugin-sdk-py/archive/master.zip
```

## Example/Usage

### Set/Get Plugin Config

You can use this SDK to save your plugin's config.
**config should not bigger than 1MB.**


```python
from dce_plugin import PluginSDK

sdk = PluginSDK()
config = {
    'key': 'Hello, World'
}

saved = sdk.set_config(config)
retrived = sdk.get_config()
```


## License
dce-plugin-sdk-py is licensed under the MIT License - see the 
[LICENSE](https://github.com/DaoCloud/dce-plugin-sdk-py/blob/master/LICENSE) file for details

# yantra

yantra is a simple plugin manager/plugin discovery framework.


## Usage

Let's assume you have a class called BaseReportPlugin which all report plugins derive from.

```python
from yantra import PluginManager, PluginType
from reports import BaseReportPlugin

# Define the type
report_type = PluginType(name='report',
                         base_class=BaseReportPlugin',
                         path='/plugins/reports/')

# Instantiate the manager
plugin_manager = PluginManager([report_type])

# Fetch plugins
plugin_manager.get_plugins(report_type)
```

You can register multiple plugin types. An alternate way to register plugin types is as follows:

```python
plugin_manager = PluginManager()
plugin_manager.register_plugin_type(foo_type)
```

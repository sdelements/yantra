import inspect
import os
from collections import namedtuple
from importlib.util import module_from_spec, spec_from_file_location

PluginType = namedtuple("PluginType", ["name", "base_class", "path"])


class PluginContainer:
    """
    A plugin container.

    Holds the plugins for a specific plugin type and has methods to discover
    them.
    """

    def __init__(self, plugin_type):
        self._plugins = []
        self._errors = {}
        self.plugin_type = plugin_type

    @property
    def errors(self):
        # clear errors from the last time we called get_plugins
        self._errors = {}

        # attempt to load the plugins and populate errors
        self.get_plugins()

        return self._errors

    def register_plugin(self, plugin_cls):
        """Register instance of the plugin class"""
        self._plugins.append(plugin_cls())

    def _get_modules(self):
        """Discover all modules in the path"""
        plugin_modules = []

        # walk the plugins folder
        for root, _, files in os.walk(self.plugin_type.path):
            for filename in files:
                modname, ext = os.path.splitext(filename)
                if ext == ".py":
                    filepath = os.path.join(root, filename)
                    spec = spec_from_file_location(modname, filepath)
                    plugin_modules.append((modname, spec))

        return plugin_modules

    def get_plugins(self):
        """Discover all plugins of the set plugin type in the path"""
        modules = self._get_modules()

        # load plugins again only if a plugin was added or removed
        if len(modules) == len(self._plugins):
            return self._plugins

        self._plugins = []

        for _modname, spec in modules:
            try:
                # load the module and look for classes
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception as e:
                error_msg = f"{e.__class__.__name__}: {str(e)}"
                self._errors[spec.origin] = error_msg
                continue

            classes_in_module = inspect.getmembers(module, inspect.isclass)

            for _, cls in classes_in_module:
                # ignore if it's the base plugin class
                if cls.__name__ == self.plugin_type.base_class.__name__:
                    continue

                # make sure that the class is a subclass of the plugin's base class
                if issubclass(cls, self.plugin_type.base_class):
                    self.register_plugin(cls)

        return self._plugins


class PluginManager:
    """
    Manager class to interact with plugins.
    """

    def __init__(self, plugin_types=None):
        self._containers = {}
        plugin_types = plugin_types or []

        for plugin_type in plugin_types:
            self.register_plugin_type(plugin_type)

    def _get_container(self, plugin_type):
        try:
            return self._containers[plugin_type.name]
        except KeyError:
            raise AssertionError(f"No plugins found for type: {plugin_type}")

    def get_errors(self, *plugin_types):
        errors = {}
        for plugin_type in plugin_types:
            errors.update(self._get_container(plugin_type).errors)
        return errors

    def register_plugin_type(self, plugin_type):
        if not isinstance(plugin_type, PluginType):
            raise TypeError("plugin_type must be an instance of PluginType")

        if plugin_type.name in self._containers:
            raise AssertionError("Plugin type with that name already exists")

        self._containers[plugin_type.name] = PluginContainer(plugin_type)

    def get_plugins(self, plugin_type):
        return self._get_container(plugin_type).get_plugins()

    def has_plugins(self, plugin_type):
        return bool(self.get_plugins(plugin_type))

    def get_plugin(self, plugin_type, plugin_id):
        return next(
            (
                plugin
                for plugin in self.get_plugins(plugin_type)
                if getattr(plugin, "id", None) == plugin_id
            ),
            None,
        )

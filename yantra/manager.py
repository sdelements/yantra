import imp
import inspect
import os


class PluginType(object):
    """
    A plugin type.
    """

    def __init__(self, name, base_class, path):
        self.name = name
        self.base_class = base_class
        self.path = path


class PluginContainer(object):
    """
    A plugin container.

    Holds the plugins for a specific plugin type and has methods to discover
    them.
    """

    def __init__(self, plugin_type):
        self._plugins = []
        self.plugin_type = plugin_type

    def register_plugin(self, plugin_cls):
        """Register instance of the plugin class"""
        self._plugins.append(plugin_cls())

    def _get_modules(self):
        """Discover all modules in the path"""
        plugin_modules = []

        # walk the plugins folder
        for root, subdir, files in os.walk(self.plugin_type.path):

            # check all sub directories
            for directory in subdir:

                directory_path = os.path.join(root, directory)
                directory_list = os.listdir(directory_path)

                for filename in directory_list:
                    modname, ext = os.path.splitext(filename)

                    if ext == ".py":
                        filename, path, desc = imp.find_module(modname, [directory_path])
                        plugin_modules.append((modname, filename, path, desc,))

        return plugin_modules

    def get_plugins(self):
        """Discover all plugins of the set plugin type in the path"""
        modules = self._get_modules()

        # load plugins again only if a plugin was added or removed
        if len(modules) == len(self._plugins):
            return self._plugins

        self._plugins = []

        for plugin_module in modules:
            modname, filename, path, desc = plugin_module

            if filename:
                # load the module and look for classes
                module = imp.load_module(modname, filename, path, desc)
                classes_in_module = inspect.getmembers(module, inspect.isclass)

                for cls in classes_in_module:
                    cls = cls[1]

                    # ignore if it's the base plugin class
                    if cls.__name__ == self.plugin_type.base_class.__name__:
                        continue

                    # make sure that the class is a subclass of the plugin's
                    # base class
                    if self.plugin_type.base_class in cls.__bases__:
                        self.register_plugin(cls)

        return self._plugins


class PluginManager(object):
    """
    Manager class to interact with plugins.
    """

    def __init__(self, plugin_types=None):
        self._containers = {}
        plugin_types = plugin_types or []

        for plugin_type in plugin_types:
            self.register_plugin_type(plugin_type)

    def register_plugin_type(self, plugin_type):
        assert isinstance(plugin_type, PluginType)

        if plugin_type.name in self._containers:
            raise AssertionError("Plugin type with that name already exists")

        self._containers[plugin_type.name] = PluginContainer(plugin_type)

    def get_plugins(self, plugin_type):
        try:
            container = self._containers[plugin_type.name]
        except KeyError:
            raise AssertionError("No plugins found for type: {0}: ".format(plugin_type))

        return container.get_plugins()

    def has_plugins(self, plugin_type):
        return bool(self.get_plugins(plugin_type))

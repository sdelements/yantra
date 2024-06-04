import unittest
from unittest.mock import MagicMock, mock_open, patch

from yantra.manager import PluginContainer, PluginManager, PluginType


class BasePlugin:
    pass


class MockPlugin(BasePlugin):
    pass


class PluginSystemTest(unittest.TestCase):
    def setUp(self):
        self.plugin_type = PluginType(
            name="test", base_class=BasePlugin, path="path/to/plugins"
        )
        self.plugin_container = PluginContainer(self.plugin_type)
        self.plugin_manager = PluginManager([self.plugin_type])

    def test_plugin_container_initialization(self):
        self.assertEqual(self.plugin_container.plugin_type, self.plugin_type)
        self.assertEqual(self.plugin_container._plugins, [])
        self.assertEqual(self.plugin_container._errors, {})

    @patch("os.walk")
    def test_plugin_discovery(self, mock_walk):
        mock_walk.return_value = [("path/to/plugins", [], ["plugin1.py", "plugin2.py"])]

        with patch("builtins.open", mock_open(read_data="")):
            with patch("importlib.util.spec_from_file_location") as mock_spec:
                mock_spec.return_value = MagicMock()
                with patch("importlib.util.module_from_spec") as mock_module:
                    mock_module.return_value = MagicMock()
                    self.plugin_container.get_plugins()
                    self.assertEqual(len(self.plugin_container._plugins), 0)

    def test_register_plugin(self):
        self.plugin_container.register_plugin(MockPlugin)
        self.assertEqual(len(self.plugin_container._plugins), 1)
        self.assertIsInstance(self.plugin_container._plugins[0], MockPlugin)

    def test_plugin_manager_initialization(self):
        self.assertIn(self.plugin_type.name, self.plugin_manager._containers)
        self.assertIsInstance(
            self.plugin_manager._containers[self.plugin_type.name], PluginContainer
        )

    def test_register_plugin_type(self):
        new_plugin_type = PluginType(
            name="new_test", base_class=BasePlugin, path="path/to/new_plugins"
        )
        self.plugin_manager.register_plugin_type(new_plugin_type)
        self.assertIn(new_plugin_type.name, self.plugin_manager._containers)

    def test_get_plugins(self):
        with patch.object(PluginContainer, "get_plugins", return_value=[MockPlugin()]):
            plugins = self.plugin_manager.get_plugins(self.plugin_type)
            self.assertEqual(len(plugins), 1)
            self.assertIsInstance(plugins[0], MockPlugin)

    def test_get_plugin(self):
        plugin_instance = MockPlugin()
        plugin_instance.id = 1
        with patch.object(
            PluginContainer, "get_plugins", return_value=[plugin_instance]
        ):
            plugin = self.plugin_manager.get_plugin(self.plugin_type, 1)
            self.assertEqual(plugin, plugin_instance)

    def test_get_errors(self):
        with patch.object(
            PluginContainer, "errors", new_callable=unittest.mock.PropertyMock
        ) as mock_errors:
            mock_errors.return_value = {"error": "Some error"}
            errors = self.plugin_manager.get_errors(self.plugin_type)
            self.assertIn("error", errors)
            self.assertEqual(errors["error"], "Some error")

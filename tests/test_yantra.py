import unittest
from yantra import PluginManager, PluginType
from tests.dummy_base_class import DummyBaseClass
from pathlib import Path


class TestYantra(unittest.TestCase):
    def test_yantra_get_plugins(self):
        tests_dir = Path(__file__).parent
        package_path = str(tests_dir) + "/test_plugins/"

        dummy_plugin_type = PluginType(
            name='dummy',
            base_class=DummyBaseClass,
            path=package_path
        )
        expected_set = {"TestClassOne", "TestClassTwo", "TestClassThree"}

        plugin_manager = PluginManager([dummy_plugin_type])

        plugins = plugin_manager.get_plugins(dummy_plugin_type)
        self.assertEqual(len(plugins), 3)
        result_set = set(plugin.name for plugin in plugins)
        self.assertEqual(result_set, expected_set)


if __name__ == '__main__':
    unittest.main()

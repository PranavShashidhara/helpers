import argparse
import os
import unittest.mock as umock
from typing import Any, Dict

try:
    from collections.abc import Hashable as AbcHashable
except ImportError:
    from collections import Hashable as AbcHashable

import pandas as pd

import config_root.config as cconfig
import helpers.hio as hio
import helpers.hpandas as hpandas
import helpers.hprint as hprint
import helpers.hserver as hserver
import helpers.hunit_test as hunitest


def _get_test_config1() -> cconfig.Config:
    """
    Build a test config for Crude Oil asset.
    """
    # Create an empty config with overwritable values.
    update_mode = "overwrite"
    config = cconfig.Config(update_mode=update_mode)
    # Add values.
    tmp_config = config.add_subconfig("build_model")
    tmp_config["activation"] = "sigmoid"
    tmp_config = config.add_subconfig("build_targets")
    tmp_config["target_asset"] = "Crude Oil"
    tmp_config = config["build_targets"].add_subconfig("preprocessing")
    tmp_config["preprocessor"] = "tokenizer"
    tmp_config = config.add_subconfig("meta")
    tmp_config["experiment_result_dir"] = "results.pkl"
    return config


def _get_test_config2() -> cconfig.Config:
    """
    Build a test config.

    Same as `_get_test_config1()` but with "Gold" instead of "Crude Oil"
    for target asset.
    """
    config = _get_test_config1().copy()
    config[("build_targets", "target_asset")] = "Gold"
    return config


def _get_test_config3() -> cconfig.Config:
    """
    Build a test config.
    """
    config = _get_test_config1().copy()
    config["hello"] = "world"
    return config


def _get_test_config4() -> cconfig.Config:
    """
    Build a test config with several key levels.
    """
    # Set config values.
    config_dict = {
        "key1": "val1",
        "key2": {
            "key2.1": {"key3.1": "val3"},
            "key2.2": 2,
        },
    }
    # Convert dict to a config with overwritable values.
    config = cconfig.Config.from_dict(config_dict)
    config.update_mode = "overwrite"
    return config


# #############################################################################
# Test_validate_configs1
# #############################################################################


# TODO(gp): -> validate_config_list
class Test_validate_configs1(hunitest.TestCase):
    def test_check_same_configs_error(self) -> None:
        """
        Verify that an error is raised when duplicated configs are encountered.
        """
        # Create list of configs with duplicates.
        configs = [
            _get_test_config1(),
            _get_test_config1(),
            _get_test_config2(),
        ]
        config_list = cconfig.ConfigList()
        # Make sure function raises an error.
        with self.assertRaises(AssertionError) as cm:
            config_list.configs = configs
        actual = str(cm.exception)
        self.check_string(actual, fuzzy_match=True)

    def test1(self) -> None:
        """
        Test configs without duplicates.
        """
        configs = [
            _get_test_config1(),
            _get_test_config2(),
            _get_test_config3(),
        ]
        config_list = cconfig.ConfigList()
        config_list.configs = configs
        config_list.validate_config_list()


# #############################################################################
# Test_apply_config_overrides_from_command_line1
# #############################################################################


class Test_apply_config_overrides_from_command_line1(hunitest.TestCase):
    def test1(self) -> None:
        """
        Verify that config values are updated correctly.
        """
        # Set test config and values to update.
        config = _get_test_config1()
        val1 = "tanh"
        val2 = "Natural Gas"
        args = argparse.Namespace(
            set_config_value=[
                f'("build_model","activation"),("{val1}")',
                f'("build_targets","target_asset"),("{val2}")',
            ]
        )
        # Run.
        actual = cconfig.apply_config_overrides_from_command_line(config, args)
        self.assertEqual(actual["build_model"]["activation"], val1)
        self.assertEqual(actual["build_targets"]["target_asset"], val2)

    def test2(self) -> None:
        """
        Verify that config values are updated correctly.
        """
        # Set test config and values to update.
        config = _get_test_config4()
        val1 = "new_val1"
        val2 = 22
        val3 = "new_val3"
        args = argparse.Namespace(
            set_config_value=[
                f'("key1"),("{val1}")',
                f'("key2","key2.2"),(int({val2}))',
                f'("key2", "key2.1", "key3.1"),("{val3}")',
            ]
        )
        # Run and check that config values are updated.
        cconfig.apply_config_overrides_from_command_line(config, args)
        self.assertEqual(config["key1"], val1)
        self.assertEqual(config["key2"]["key2.2"], val2)
        self.assertEqual(config["key2"]["key2.1"]["key3.1"], val3)


# #############################################################################
# Test_intersect_configs1
# #############################################################################


class Test_intersect_configs1(hunitest.TestCase):
    def test_same_config(self) -> None:
        """
        Verify that intersection of two same configs equals those configs.
        """
        # Prepare test config.
        config = _get_test_config1()
        # FInd intersection of two same configs.
        actual = cconfig.intersect_configs([config, config])
        # Verify that intersection is equal to initial config.
        self.assertEqual(str(actual), str(config))

    def test1(self) -> None:
        """
        Verify that intersection of two different configs is what is expected.
        """
        config1 = _get_test_config1()
        config2 = _get_test_config2()
        intersection = cconfig.intersect_configs([config1, config2])
        actual = str(intersection)
        expected = r"""
        build_model:
          activation: sigmoid
        build_targets:
          preprocessing:
            preprocessor: tokenizer
        meta:
          experiment_result_dir: results.pkl"""
        expected = hprint.dedent(expected)
        self.assert_equal(actual, expected, fuzzy_match=False)


# #############################################################################
# Test_subtract_configs1
# #############################################################################


class Test_subtract_configs1(hunitest.TestCase):
    def test_same_config(self) -> None:
        """
        Verify that the difference of two configs is empty.
        """
        config = _get_test_config1()
        diff = cconfig.subtract_config(config, config)
        # The difference should be empty.
        self.assertFalse(diff)

    def test1(self) -> None:
        """
        Verify that differing parameters of different configs are what
        expected.
        """
        config1 = _get_test_config1()
        config2 = _get_test_config2()
        actual = cconfig.subtract_config(config1, config2)
        expected = """
        build_targets:
          target_asset: Crude Oil"""
        expected = hprint.dedent(expected)
        self.assert_equal(str(actual), str(expected))

    def test2(self) -> None:
        """
        Both configs contain an empty dict.
        """
        config_dict1 = {
            "key1": [
                (
                    2,
                    "value3",
                    {},
                )
            ],
            "key2": {},
        }
        config_dict2 = {
            "key1": [
                (
                    (1, 3),
                    "value3",
                    None,
                )
            ],
            "key2": {},
        }
        config1 = cconfig.Config().from_dict(config_dict1)
        config2 = cconfig.Config().from_dict(config_dict2)
        actual = cconfig.subtract_config(config1, config2)
        # An empty dict
        expected = r"""
        key1: [(2, 'value3', {})]
        key2:
        """
        self.assert_equal(str(actual), expected, fuzzy_match=True)

    def test3(self) -> None:
        """
        A config contains a non-empty empty dict.
        """
        config_dict1 = {
            "key1": {"key2": "value2", "key3": {"key4": "value3", "key5": 5}}
        }
        config_dict2 = {
            "key1": {
                "key3": "value3",
            },
            "key2": {},
        }
        config1 = cconfig.Config().from_dict(config_dict1)
        config2 = cconfig.Config().from_dict(config_dict2)
        actual = cconfig.subtract_config(config1, config2)
        expected = r"""
        key1:
          key2: value2
          key3:
            key4: value3
            key5: 5
        """
        self.assert_equal(str(actual), expected, fuzzy_match=True)


# #############################################################################
# Test_diff_configs1
# #############################################################################


class Test_diff_configs1(hunitest.TestCase):
    def test_same_config(self) -> None:
        """
        Verify that the difference of two configs is empty.
        """
        config = _get_test_config1()
        actual = cconfig.diff_configs([config, config])
        expected = [cconfig.Config(), cconfig.Config()]
        self.assert_equal(str(actual), str(expected))

    def test1(self) -> None:
        config1 = _get_test_config1()
        expected = """
        build_model:
          activation: sigmoid
        build_targets:
          target_asset: Crude Oil
          preprocessing:
            preprocessor: tokenizer
        meta:
          experiment_result_dir: results.pkl"""
        expected = hprint.dedent(expected)
        self.assert_equal(str(config1), expected)
        #
        config2 = _get_test_config2()
        expected = """
        build_model:
          activation: sigmoid
        build_targets:
          target_asset: Gold
          preprocessing:
            preprocessor: tokenizer
        meta:
          experiment_result_dir: results.pkl"""
        expected = hprint.dedent(expected)
        self.assert_equal(str(config2), expected)
        #
        actual = cconfig.diff_configs([config1, config2])
        expected = [
            #
            cconfig.Config.from_dict(
                {"build_targets": {"target_asset": "Crude Oil"}}
            ),
            #
            cconfig.Config.from_dict(
                {"build_targets": {"target_asset": "Gold"}}
            ),
        ]
        self.assert_equal(str(actual), str(expected))

    def test2(self) -> None:
        config1 = _get_test_config1()
        config2 = _get_test_config2()
        config3 = _get_test_config3()
        #
        actual = cconfig.diff_configs([config1, config2, config3])
        actual = "\n".join(map(str, actual))
        #
        expected = [
            #
            cconfig.Config.from_dict(
                {"build_targets": {"target_asset": "Crude Oil"}}
            ),
            #
            cconfig.Config.from_dict(
                {"build_targets": {"target_asset": "Gold"}}
            ),
            #
            cconfig.Config.from_dict(
                {
                    "build_targets": {"target_asset": "Crude Oil"},
                    "hello": "world",
                }
            ),
        ]
        expected = "\n".join(map(str, expected))
        self.assert_equal(str(actual), str(expected))


# #############################################################################
# Test_convert_to_dataframe1
# #############################################################################


class Test_convert_to_dataframe1(hunitest.TestCase):
    def test1(self) -> None:
        """
        Compute and verify dataframe with all config parameters.
        """
        config1 = _get_test_config1()
        config2 = _get_test_config2()
        # Convert configs to dataframe.
        actual = cconfig.convert_to_dataframe([config1, config2])
        actual = hpandas.df_to_str(actual, num_rows=None)
        #
        expected = pd.DataFrame(
            {
                "build_model.activation": ["sigmoid", "sigmoid"],
                "build_targets.target_asset": ["Crude Oil", "Gold"],
                "build_targets.preprocessing.preprocessor": [
                    "tokenizer",
                    "tokenizer",
                ],
                "meta.experiment_result_dir": ["results.pkl", "results.pkl"],
            }
        )
        expected = hpandas.df_to_str(expected, num_rows=None)
        self.assert_equal(str(actual), str(expected))


# #############################################################################
# Test_build_config_diff_dataframe1
# #############################################################################


class Test_build_config_diff_dataframe1(hunitest.TestCase):
    def test1(self) -> None:
        """
        Summarize differences between two different configs.
        """
        config1 = _get_test_config1()
        config2 = _get_test_config2()
        #
        actual = cconfig.build_config_diff_dataframe(
            {"1": config1, "2": config2}
        )
        actual = hpandas.df_to_str(actual, num_rows=None)
        #
        expected = pd.DataFrame(
            {
                "build_targets.target_asset": ["Crude Oil", "Gold"],
            }
        )
        expected = hpandas.df_to_str(expected, num_rows=None)
        self.assert_equal(str(actual), str(expected))

    def test2(self) -> None:
        """
        Same config.
        """
        config1 = _get_test_config1()
        #
        actual = cconfig.build_config_diff_dataframe(
            {"1": config1, "2": config1}
        )
        actual = hpandas.df_to_str(actual, num_rows=None)
        #
        expected = """
        Empty DataFrame
        Columns: []
        Index: [0, 1]
        """
        self.assert_equal(str(actual), expected, fuzzy_match=True)

    def test3(self) -> None:
        """
        Three different configs.
        """
        config1 = _get_test_config1()
        config2 = _get_test_config2()
        config3 = _get_test_config3()
        #
        actual = cconfig.build_config_diff_dataframe(
            {"1": config1, "2": config2, "3": config3}
        )
        actual = hpandas.df_to_str(actual, num_rows=None)
        #
        expected = """
          build_targets.target_asset  hello
        0                  Crude Oil    NaN
        1                       Gold    NaN
        2                  Crude Oil  world
        """
        self.assert_equal(str(actual), expected, fuzzy_match=True)


# #############################################################################
# Test_make_hashable
# #############################################################################


class Test_make_hashable(hunitest.TestCase):
    def helper(self, obj: Any, is_hashable: bool, expected: str) -> None:
        is_hashable_before = isinstance(obj, AbcHashable)
        self.assertEqual(is_hashable_before, is_hashable)
        #
        hashable_obj = cconfig.make_hashable(obj)
        is_hashable_after = isinstance(hashable_obj, AbcHashable)
        self.assertTrue(is_hashable_after)
        #
        actual = str(hashable_obj)
        self.assert_equal(actual, expected, fuzzy_match=True)

    def test1(self) -> None:
        """
        Test an unhashable nested object.
        """
        obj = [
            (
                2,
                {
                    "key": "value",
                    "key2": "value2",
                    "key3": 4,
                },
                "value3",
                {},
            )
        ]
        is_hashable = False
        expected = "((2, (('key', 'value'), ('key2', 'value2'), ('key3', 4)), 'value3', ()),)"
        self.helper(obj, is_hashable, expected)

    def test2(self) -> None:
        """
        Test an unhashable nested object.
        """
        obj = {
            1: [
                "value1",
                {},
                {
                    "key2": {},
                    "key3": (3, "4", [5, {6: "7"}]),
                },
            ],
            (8, 9, 0): "value2",
            "key4": [],
        }
        is_hashable = False
        expected = r"""
        ((1, ('value1', (), (('key2', ()), ('key3', (3, '4', (5, ((6, '7'),))))))), ((8, 9, 0), 'value2'), ('key4', ()))
        """
        self.helper(obj, is_hashable, expected)

    def test3(self) -> None:
        """
        Test a nested Tuple.
        """
        obj = (
            1,
            ["2", 3],
        )
        is_hashable = True
        expected = r"(1, ('2', 3))"
        self.helper(obj, is_hashable, expected)

    def test4(self) -> None:
        """
        Test a dictionary.
        """
        obj = {
            1: "2",
        }
        is_hashable = False
        expected = r"((1, '2'),)"
        self.helper(obj, is_hashable, expected)

    def test5(self) -> None:
        """
        Test a string.
        """
        obj = "1"
        is_hashable = True
        expected = r"1"
        self.helper(obj, is_hashable, expected)

    def test6(self) -> None:
        """
        Test a hashable object.
        """
        obj = 2
        is_hashable = True
        expected = r"2"
        self.helper(obj, is_hashable, expected)


# #############################################################################
# Test_replace_shared_root_path
# #############################################################################


class Test_replace_shared_root_path(hunitest.TestCase):
    def test_replace_shared_dir_paths(self) -> None:
        """
        Test replacing in config all shared root paths with the dummy mapping.
        """
        # Mock `hserver.get_shared_data_dirs()` to return a dummy mapping.
        mock_mapping = {
            "/ecs_tokyo": "/ecs",
            "/data/shared1": "/shared_folder1",
            "/data/shared2": "/shared_folder2",
        }
        with umock.patch.object(
            hserver,
            "get_shared_data_dirs",
            return_value=mock_mapping,
        ):
            # Initial Config.
            initial_config = cconfig.Config.from_dict(
                {
                    "key1": "/data/shared1/asset1",
                    "key2": "/data/shared2/asset1/item",
                    "key3": 1,
                    "key4": 'object("/data/shared2/asset1/item")',
                    "key5": {
                        "key5.1": "/data/shared1/asset1",
                        "key5.2": "/data/shared2/asset2",
                    },
                    "key6": "/data/shared1/ecs_tokyo/some_path",
                }
            )
            actual_config = cconfig.replace_shared_dir_paths(initial_config)
            # Check that shared root paths have been replaced.
            actual = str(actual_config)
            expected = """
                key1: /shared_folder1/asset1
                key2: /shared_folder2/asset1/item
                key3: 1
                key4: object("/shared_folder2/asset1/item")
                key5:
                key5.1: /shared_folder1/asset1
                key5.2: /shared_folder2/asset2
                key6: /shared_folder1/ecs/some_path
            """
            self.assert_equal(actual, expected, fuzzy_match=True)


# #############################################################################
# Test_load_config_from_pickle1
# #############################################################################


class Test_load_config_from_pickle1(hunitest.TestCase):
    def helper(
        self, expected_config_version: str, expected_signature: str
    ) -> None:
        # Set config.
        log_dir = self.get_scratch_space()
        tag = "system_config.output"
        nested: Dict[str, Any] = {
            "key1": "val",
            "key2": {"key3": {"key4": [1, 2, 3]}},
        }
        config = cconfig.Config.from_dict(nested)
        # Save config and related files.
        config.save_to_file(log_dir, tag)
        # Check config version file for different config versions.
        config_version_path = os.path.join(log_dir, "config_version.txt")
        if expected_config_version == "v2":
            # v2 config version has no file with info about it.
            hio.delete_file(config_version_path)
        else:
            # Check config version.
            actual_config_version = hio.from_file(config_version_path)
            self.assert_equal(actual_config_version, expected_config_version)
        # Load config from the file.
        actual = cconfig.load_config_from_pickle1(log_dir, tag)
        # Check signature.
        actual_signature = str(actual)
        self.assert_equal(actual_signature, expected_signature, fuzzy_match=True)

    def test_v2_config1(self) -> None:
        """
        Check that v2 config is extracted correctly.
        """
        expected_config_version = "v2"
        # Integer values are extracted as strings as expected for v2.
        expected_signature = r"""
        key1: val
        key2:
            key3:
                key4: ['1', '2', '3']
        """
        self.helper(expected_config_version, expected_signature)

    def test_v3_config1(self) -> None:
        """
        Check that v3 config is extracted correctly.
        """
        expected_config_version = "v3"
        # Integer values are extracted in original format as expected for v3.
        expected_signature = r"""
        key1: val
        key2:
            key3:
                key4: [1, 2, 3]
        """
        self.helper(expected_config_version, expected_signature)

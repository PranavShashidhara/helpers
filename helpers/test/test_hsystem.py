import logging
import os
import re
import tempfile
from typing import List

import helpers.hdbg as hdbg
import helpers.hio as hio
import helpers.hsystem as hsystem
import helpers.hunit_test as hunitest
import helpers.hunit_test_purification as huntepur

_LOG = logging.getLogger(__name__)

# #############################################################################


# #############################################################################
# Test_system1
# #############################################################################


class Test_system1(hunitest.TestCase):
    def test1(self) -> None:
        hsystem.system("ls")

    def test2(self) -> None:
        hsystem.system("ls /dev/null", suppress_output=False)

    def test3(self) -> None:
        """
        Output to a file.
        """
        with tempfile.NamedTemporaryFile() as fp:
            temp_file_name = fp.name
            _LOG.debug("temp_file_name=%s", temp_file_name)
            hsystem.system("ls", output_file=temp_file_name)
            hdbg.dassert_path_exists(temp_file_name)

    def test4(self) -> None:
        """
        Tee to a file.
        """
        with tempfile.NamedTemporaryFile() as fp:
            temp_file_name = fp.name
            _LOG.debug("temp_file_name=%s", temp_file_name)
            hsystem.system("ls", output_file=temp_file_name, tee=True)
            hdbg.dassert_path_exists(temp_file_name)

    def test5(self) -> None:
        """
        Test dry_run.
        """
        temp_file_name = tempfile._get_default_tempdir()  # type: ignore
        candidate_name = tempfile._get_candidate_names()  # type: ignore
        temp_file_name += "/" + next(candidate_name)
        _LOG.debug("temp_file_name=%s", temp_file_name)
        hsystem.system("ls", output_file=temp_file_name, dry_run=True)
        hdbg.dassert_path_not_exists(temp_file_name)

    def test6(self) -> None:
        """
        Test abort_on_error=True.
        """
        hsystem.system("ls this_file_doesnt_exist", abort_on_error=False)

    def test7(self) -> None:
        """
        Test abort_on_error=False.
        """
        with self.assertRaises(RuntimeError) as cm:
            hsystem.system("ls this_file_doesnt_exist")
        actual = str(cm.exception)
        # Different systems return different rc.
        # cmd='(ls this_file_doesnt_exist) 2>&1' failed with rc='2'
        actual = re.sub(r"rc='(\d+)'", "rc=''", actual)
        self.check_string(actual)

    def test8(self) -> None:
        """
        Check that an assert error is raised when `tee` is passed without a log
        file.
        """
        with self.assertRaises(AssertionError) as cm:
            _ = hsystem.system("ls this_should_fail", tee=True)
        actual = str(cm.exception)
        expected = r"""
        ################################################################################
        * Failed assertion *
        'True' implies 'False'
        ################################################################################
        """
        self.assert_equal(actual, expected, fuzzy_match=True)

    def test9(self) -> None:
        """
        Check that the failing command fails and logs are stored in the log
        file.

        - `allow_errors = False`
        - `tee = True`
        - Log file path is passed
        """
        log_dir = self.get_scratch_space()
        log_file_path = os.path.join(log_dir, "tee_log")
        with self.assertRaises(RuntimeError) as cm:
            _ = hsystem.system(
                "ls this_should_fail", tee=True, output_file=log_file_path
            )
        actual = str(cm.exception)
        text_purifier = huntepur.TextPurifier()
        actual = text_purifier.purify_txt_from_client(actual)
        expected = r"""

        ################################################################################
        ################################################################################
        _system() failed
        ################################################################################
        ################################################################################
        # _system: cmd='(ls this_should_fail) 2>&1 | tee -a $GIT_ROOT/helpers/test/outcomes/Test_system1.test9/tmp.scratch/tee_log; exit ${PIPESTATUS[0]}', abort_on_error=True, suppress_error=None, suppress_output=True, blocking=True, wrapper=None, output_file='$GIT_ROOT/helpers/test/outcomes/Test_system1.test9/tmp.scratch/tee_log', num_error_lines=30, tee=True, dry_run=False, log_level=10
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        cmd='(ls this_should_fail) 2>&1 | tee -a $GIT_ROOT/helpers/test/outcomes/Test_system1.test9/tmp.scratch/tee_log; exit ${PIPESTATUS[0]}'
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        - rc='2'
        - output='
        ls: cannot access 'this_should_fail': No such file or directory
        '
        - Output saved in 'tmp.system_output.txt'
        - Command saved in 'tmp.system_cmd.sh'
        """
        self.assert_equal(actual, expected, fuzzy_match=True)
        # Check log output.
        actual = hio.from_file(log_file_path)
        expected = r"""
        ls: cannot access 'this_should_fail': No such file or directory
        """
        self.assert_equal(actual, expected, fuzzy_match=True, dedent=True)

    def test10(self) -> None:
        """
        Check that the failing command passes and logs are stored in the log
        file.

        - `allow_errors = True`
        - `tee = True`
        - Log file path is passed
        """
        log_dir = self.get_scratch_space()
        log_file_path = os.path.join(log_dir, "tee_log")
        rc = hsystem.system(
            "ls this_should_fail",
            tee=True,
            abort_on_error=False,
            output_file=log_file_path,
        )
        self.assertNotEqual(rc, 0)
        # Check log output.
        actual = hio.from_file(log_file_path)
        expected = (
            r"ls: cannot access 'this_should_fail': No such file or directory\n"
        )
        self.assert_equal(actual, expected, fuzzy_match=True)


# #############################################################################


# #############################################################################
# Test_system2
# #############################################################################


class Test_system2(hunitest.TestCase):
    def test_get_user_name(self) -> None:
        actual = hsystem.get_user_name()
        _LOG.debug("actual=%s", actual)
        #
        expected = hsystem.system_to_string("whoami")[1]
        _LOG.debug("expected=%s", expected)
        self.assertEqual(actual, expected)
        #
        expected = hsystem.system_to_one_line("whoami")[1]
        _LOG.debug("expected=%s", expected)
        self.assertEqual(actual, expected)

    def test_get_server_name(self) -> None:
        actual = hsystem.get_server_name()
        _LOG.debug("actual=%s", actual)
        #
        expected = hsystem.system_to_string("uname -n")[1]
        _LOG.debug("expected=%s", expected)
        self.assertEqual(actual, expected)

    def test_get_os_name(self) -> None:
        actual = hsystem.get_os_name()
        _LOG.debug("actual=%s", actual)
        #
        expected = hsystem.system_to_string("uname -s")[1]
        _LOG.debug("expected=%s", expected)
        self.assertEqual(actual, expected)


# #############################################################################


# #############################################################################
# Test_compute_file_signature1
# #############################################################################


class Test_compute_file_signature1(hunitest.TestCase):
    def test1(self) -> None:
        """
        Compute the signature of a file using 1 enclosing dir.
        """
        file_name = (
            "/app/amp/core/test/TestCheckSameConfigs."
            + "test_check_same_configs_error/output/test.txt"
        )
        dir_depth = 1
        actual = hsystem._compute_file_signature(file_name, dir_depth=dir_depth)
        expected = ["output", "test.txt"]
        self.assert_equal(str(actual), str(expected))

    def test2(self) -> None:
        """
        Compute the signature of a file using 2 enclosing dirs.
        """
        file_name = (
            "/app/amp/core/test/TestCheckSameConfigs."
            + "test_check_same_configs_error/output/test.txt"
        )
        dir_depth = 2
        actual = hsystem._compute_file_signature(file_name, dir_depth=dir_depth)
        expected = [
            "TestCheckSameConfigs.test_check_same_configs_error",
            "output",
            "test.txt",
        ]
        self.assert_equal(str(actual), str(expected))

    def test3(self) -> None:
        """
        Compute the signature of a file using 4 enclosing dirs.
        """
        file_name = "/app/amp/core/test/TestApplyAdfTest.test1/output/test.txt"
        dir_depth = 4
        actual = hsystem._compute_file_signature(file_name, dir_depth=dir_depth)
        expected = [
            "core",
            "test",
            "TestApplyAdfTest.test1",
            "output",
            "test.txt",
        ]
        self.assert_equal(str(actual), str(expected))


# #############################################################################


# #############################################################################
# Test_find_file_with_dir1
# #############################################################################


class Test_find_file_with_dir1(hunitest.TestCase):
    def test1(self) -> None:
        """
        Check whether we can find this file using one enclosing dir.
        """
        # Use this file.
        file_name = "helpers/test/test_hsystem.py"
        dir_depth = 1
        actual = hsystem.find_file_with_dir(file_name, dir_depth=dir_depth)
        expected = r"""['helpers/test/test_hsystem.py']"""
        self.assert_equal(str(actual), str(expected), purify_text=True)

    def test2(self) -> None:
        """
        Check whether we can find a test golden output using different number
        of enclosing dirs.

        With only 1 enclosing dir, we can't find it.
        """
        # Use only one dir which is not enough to identify the file.
        # E.g., .../test/TestSqlWriterBackend1.test_insert_tick_data1/output/test.txt
        dir_depth = 1
        mode = "return_all_results"
        actual = self._helper(dir_depth, mode)
        # For sure there are more than 100 tests.
        self.assertGreater(len(actual), 100)

    def test3(self) -> None:
        """
        Like `test2`, but using 2 levels for sure we are going to identify the
        file.
        """
        dir_depth = 2
        mode = "return_all_results"
        actual = self._helper(dir_depth, mode)
        _LOG.debug("Found %d matching files", len(actual))
        # There should be a single match.
        expected = r"""['helpers/test/outcomes/Test_find_file_with_dir1.test3/output/test.txt']"""
        self.assert_equal(str(actual), str(expected), purify_text=True)
        self.assertEqual(len(actual), 1)

    def test4(self) -> None:
        """
        Like `test2`, but using 2 levels for sure we are going to identify the
        file and asserting in case we don't find a single result.
        """
        dir_depth = 2
        mode = "assert_unless_one_result"
        actual = self._helper(dir_depth, mode)
        _LOG.debug("Found %d matching files", len(actual))
        # There should be a single match.
        expected = r"""['helpers/test/outcomes/Test_find_file_with_dir1.test4/output/test.txt']"""
        self.assert_equal(str(actual), str(expected), purify_text=True)
        self.assertEqual(len(actual), 1)

    def test5(self) -> None:
        """
        Like `test2`, using more level than 2, again, we should have a single
        result.
        """
        dir_depth = 3
        mode = "assert_unless_one_result"
        actual = self._helper(dir_depth, mode)
        _LOG.debug("Found %d matching files", len(actual))
        expected = r"""['helpers/test/outcomes/Test_find_file_with_dir1.test5/output/test.txt']"""
        self.assert_equal(str(actual), str(expected), purify_text=True)
        self.assertEqual(len(actual), 1)

    def _helper(self, dir_depth: int, mode: str) -> List[str]:
        # Create a fake golden outcome to be used in this test.
        actual = "hello world"
        self.check_string(actual)
        # E.g., helpers/test/test_hsystem.py::Test_find_file_with_dir1::test2/test.txt
        file_name = os.path.join(self.get_output_dir(), "test.txt")
        _LOG.debug("file_name=%s", file_name)
        actual: List[str] = hsystem.find_file_with_dir(
            file_name, dir_depth=dir_depth, mode=mode
        )
        _LOG.debug("Found %d matching files", len(actual))
        return actual


# #############################################################################


# #############################################################################
# Test_Linux_commands1
# #############################################################################


class Test_Linux_commands1(hunitest.TestCase):
    def test_du1(self) -> None:
        hsystem.du(".")


# #############################################################################


# #############################################################################
# Test_has_timestamp1
# #############################################################################


class Test_has_timestamp1(hunitest.TestCase):
    def test_has_not_timestamp1(self) -> None:
        """
        No timestamp.
        """
        file_name = "patch.amp.8c5a2da9.tgz"
        actual = hsystem.has_timestamp(file_name)
        expected = False
        self.assertEqual(actual, expected)

    def test_has_timestamp1(self) -> None:
        """
        Valid timestamp.
        """
        file_name = "patch.amp.8c5a2da9.20210725_225857.tgz"
        actual = hsystem.has_timestamp(file_name)
        expected = True
        self.assertEqual(actual, expected)

    def test_has_timestamp2(self) -> None:
        """
        Valid timestamp.
        """
        file_name = "/foo/bar/patch.amp.8c5a2da9.20210725-22_58_57.tgz"
        actual = hsystem.has_timestamp(file_name)
        expected = True
        self.assertEqual(actual, expected)

    def test_has_timestamp3(self) -> None:
        """
        Valid timestamp.
        """
        file_name = "/foo/bar/patch.amp.8c5a2da9.20210725225857.tgz"
        actual = hsystem.has_timestamp(file_name)
        expected = True
        self.assertEqual(actual, expected)

    def test_has_timestamp4(self) -> None:
        """
        Valid timestamp.
        """
        file_name = "/foo/bar/patch.amp.8c5a2da9.20210725_22_58_57.tgz"
        actual = hsystem.has_timestamp(file_name)
        expected = True
        self.assertEqual(actual, expected)

    def test_has_timestamp5(self) -> None:
        """
        Valid timestamp.
        """
        file_name = "/foo/bar/patch.amp.8c5a2da9.20210725225857.tgz"
        actual = hsystem.has_timestamp(file_name)
        expected = True
        self.assertEqual(actual, expected)


# #############################################################################
# Test_append_timestamp_tag1
# #############################################################################


class Test_append_timestamp_tag1(hunitest.TestCase):
    def test_no_timestamp1(self) -> None:
        """
        Invalid timestamp, with no tag.
        """
        file_name = "/foo/bar/patch.amp.8c5a2da9.tgz"
        tag = ""
        actual = hsystem.append_timestamp_tag(file_name, tag)
        # /foo/bar/patch.amp.8c5a2da9.20210726-15_11_25.tgz
        expected = r"/foo/bar/patch.amp.8c5a2da9.\S+.tgz"
        self.assertRegex(actual, expected)

    def test_no_timestamp2(self) -> None:
        """
        Invalid timestamp, with no tag.
        """
        file_name = "/foo/bar/patch.amp.8c5a2da9.tgz"
        tag = "hello"
        actual = hsystem.append_timestamp_tag(file_name, tag)
        # /foo/bar/patch.amp.8c5a2da9.20210726-15_11_25.hello.tgz
        expected = r"/foo/bar/patch.amp.8c5a2da9.\S+.hello.tgz"
        self.assertRegex(actual, expected)

    def test1(self) -> None:
        """
        Valid timestamp, with no tag.
        """
        file_name = "/foo/bar/patch.amp.8c5a2da9.20210725_225857.tgz"
        tag = ""
        actual = hsystem.append_timestamp_tag(file_name, tag)
        # /foo/bar/patch.amp.8c5a2da9.20210725_225857.20210726-15_11_25.tgz
        expected = "/foo/bar/patch.amp.8c5a2da9.20210725_225857.tgz"
        self.assertEqual(actual, expected)

    def test2(self) -> None:
        """
        Valid timestamp, with a tag.
        """
        file_name = "/foo/bar/patch.amp.8c5a2da9.20210725_225857.tgz"
        tag = "hello"
        actual = hsystem.append_timestamp_tag(file_name, tag)
        expected = "/foo/bar/patch.amp.8c5a2da9.20210725_225857.hello.tgz"
        self.assertEqual(actual, expected)

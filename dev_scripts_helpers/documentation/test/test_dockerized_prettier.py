import os

import pytest

import helpers.hdockerized_executables as hdocexec
import helpers.hio as hio
import helpers.hprint as hprint
import helpers.hserver as hserver
import helpers.hunit_test as hunitest


# #############################################################################
# Test_run_dockerized_prettier
# #############################################################################


@pytest.mark.skipif(
    hserver.is_inside_ci() or hserver.is_dev_csfy(),
    reason="Disabled because of CmampTask10710",
)
class Test_run_dockerized_prettier(hunitest.TestCase):
    def test1(self) -> None:
        """
        Test that Dockerized Prettier reads an input file, formats it, and
        writes the output file in the output directory.
        """
        input_dir = self.get_input_dir()
        output_dir = self.get_output_dir()
        hio.create_dir(output_dir, incremental=True)
        input_file_path = os.path.join(input_dir, "input.md")
        output_file_path = os.path.join(output_dir, "output.md")
        # Prepare input command options.
        cmd_opts = [
            "--parser",
            "markdown",
            "--prose-wrap",
            "always",
            "--tab-width",
            "2",
        ]
        # Call function to test.
        hdocexec.run_dockerized_prettier(
            input_file_path,
            cmd_opts,
            output_file_path,
            file_type="md",
            mode="system",
            force_rebuild=False,
            use_sudo=False,
        )
        # Check output.
        self.assertTrue(
            os.path.exists(output_file_path),
            "Output file was not created by Dockerized Prettier.",
        )

    def test_prettier_on_str1(self) -> None:
        """
        Test that Dockerized Prettier reads an input file, formats it, and
        writes the output file in the output directory.
        """
        text = """
        # Title
        hello!

        ## Content
        """
        text = hprint.dedent(text)
        cmd_opts = [
            "--parser",
            "markdown",
            "--prose-wrap",
            "always",
            "--tab-width",
            "2",
        ]
        # Call function to test.
        actual = hdocexec.prettier_on_str(
            text,
            file_type="md",
            cmd_opts=cmd_opts,
            mode="system",
            force_rebuild=False,
            use_sudo=False,
        )
        # Check output.
        expected = """
        # Title

        hello!

        ## Content
        """
        self.assert_equal(actual, expected, dedent=True)

#!/usr/bin/env python3

"""
Extract headers from a Markdown file and generate a Vim cfile.

The script:
- processes the input Markdown file
- extracts headers up to a specified maximum level
- prints a human-readable header map
- generates an output file in a format that can be used with Vim's quickfix
  feature.

# Extract headers up to level 3 from a Markdown file and save to an output file:
> extract_headers_from_markdown.py -i input.md -o cfile --mode cfile --max-level 3

# Extract headers up to level 2 and print to stdout:
> extract_headers_from_markdown.py -i input.md -o - --mode headers

# To use the generated cfile in Vim:
- Open Vim and run `:cfile output.cfile`
  ```
  > vim -c "cfile cfile"
  ```
- Navigate between headers using `:cnext` and `:cprev`
"""

import argparse
import logging
from typing import List

import helpers.hdbg as hdbg
import helpers.hmarkdown as hmarkdo
import helpers.hparser as hparser

_LOG = logging.getLogger(__name__)


def _extract_headers_from_markdown(
    lines: List[str],
    mode: str,
    max_level: int,
    out_file_name: str,
) -> None:
    """
    Extract headers from a Markdown file.
    """
    hdbg.dassert_isinstance(lines, list)
    # We don't want to sanity check since we want to show the headers, even
    # if malformed.
    sanity_check = False
    header_list = hmarkdo.extract_headers_from_markdown(
        lines, max_level=max_level, sanity_check=sanity_check
    )
    # Print the headers.
    if mode == "cfile":
        output_content = hmarkdo.header_list_to_vim_cfile(lines, header_list)
    else:
        output_content = hmarkdo.header_list_to_markdown(header_list, mode)
    hparser.write_file(output_content, out_file_name)
    # Sanity check the headers.
    hmarkdo.sanity_check_header_list(header_list)


# TODO(gp): _parse() -> _build_parser() everywhere.
def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Print to stdout by default.
    out_default = "-"
    hparser.add_input_output_args(parser, out_default=out_default)
    parser.add_argument(
        "--mode",
        type=str,
        default="list",
        choices=["list", "headers", "cfile"],
        help="Output mode",
    )
    parser.add_argument(
        "--max_level",
        type=int,
        default=3,
        help="Maximum header levels to parse",
    )
    hparser.add_verbosity_arg(parser)
    return parser


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    # Do not print information.
    verbose = False
    hparser.init_logger_for_input_output_transform(args, verbose=verbose)
    in_file_name, out_file_name = hparser.parse_input_output_args(args)
    #
    input_content = hparser.read_file(in_file_name)
    _extract_headers_from_markdown(
        input_content, args.mode, args.max_level, out_file_name
    )


if __name__ == "__main__":
    _main(_parse())

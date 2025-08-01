"""
Import as:

import helpers.hstring as hstring
"""

import logging
import os
import re
import tempfile
from typing import List, Optional, Tuple

import helpers.hdbg as hdbg
import helpers.hio as hio
import helpers.hsystem as hsystem

_LOG = logging.getLogger(__name__)


def remove_prefix(string: str, prefix: str, assert_on_error: bool = True) -> str:
    if string.startswith(prefix):
        res = string[len(prefix) :]
    else:
        res = string
        if assert_on_error:
            raise RuntimeError(
                f"string='{string}' doesn't start with prefix ='{prefix}'"
            )
    return res


def remove_suffix(string: str, suffix: str, assert_on_error: bool = True) -> str:
    if string.endswith(suffix):
        res = string[: -len(suffix)]
    else:
        res = string
        if assert_on_error:
            raise RuntimeError(
                f"string='{string}' doesn't end with suffix='{suffix}'"
            )
    return res


def diff_strings(
    txt1: str,
    txt2: str,
    txt1_descr: Optional[str] = None,
    txt2_descr: Optional[str] = None,
    width: int = 130,
) -> str:
    # Write file.
    def _to_file(txt: str, txt_descr: Optional[str]) -> str:
        file_name = tempfile.NamedTemporaryFile().name
        if txt_descr is not None:
            txt = "# " + txt_descr + "\n" + txt
        hio.to_file(file_name, txt)
        return file_name

    file_name1 = _to_file(txt1, txt1_descr)
    file_name2 = _to_file(txt2, txt2_descr)
    # Get the difference between the files.
    cmd = f"sdiff --width={width} {file_name1} {file_name2}"
    _, txt = hsystem.system_to_string(
        cmd,
        # We don't care if they are different.
        abort_on_error=False,
    )
    return txt


# TODO(gp): GFI. Move to hpython_code.py
def get_docstring_line_indices(lines: List[str]) -> List[int]:
    """
    Get indices of lines of code that are inside (doc)strings.

    :param lines: the code lines to check
    :return: the indices of docstrings
    """
    docstring_line_indices = []
    quotes = {'"""': False, "'''": False, "```": False}
    for i, line in enumerate(lines):
        # Determine if the current line is inside a (doc)string.
        for quote in quotes:
            quotes_matched = re.findall(quote, line)
            for q in quotes_matched:
                # Switch the docstring flag.
                # pylint: disable=modified-iterating-dict
                quotes[q] = not quotes[q]
                if q in ('"""', "'''") and not quotes[q]:
                    # A triple-quote has just been closed.
                    # Reset the triple backticks flag.
                    quotes["```"] = False
        if any(quotes.values()):
            # Store the index if the quotes have been opened but not closed yet.
            docstring_line_indices.append(i)
    return docstring_line_indices


def get_docstrings(lines: List[str]) -> List[List[int]]:
    """
    Get line indices grouped together by the docstring they belong to.

    :param lines: lines from the file to process
    :return: grouped lines within docstrings
    """
    # Get indices of lines that are within docstrings.
    doc_indices = get_docstring_line_indices(lines)
    # Group these indices into consecutive docstrings.
    docstrings = []
    if doc_indices:
        current_docstring = [doc_indices[0]]
        for idx in doc_indices[1:]:
            if idx == current_docstring[-1] + 1:
                current_docstring.append(idx)
            else:
                docstrings.append(current_docstring)
                current_docstring = [idx]
        docstrings.append(current_docstring)
    return docstrings


# TODO(gp): GFI. Move to hpython_code.py
def get_code_block_line_indices(lines: List[str]) -> List[int]:
    """
    Get indices of lines that are inside code blocks.

    Code blocks are lines surrounded by triple backticks, e.g.,
    ```
    This line.
    ```
    Note that the backticks need to be the leftmost element of their line.

    :param lines: the lines to check
    :return: the indices of code blocks
    """
    code_block_line_indices = []
    quotes = {"```": False}
    for i, line in enumerate(lines):
        # Determine if the current line is inside a code block.
        for quote in quotes:
            quotes_matched = re.findall(rf"^\s*({quote})", line)
            for q in quotes_matched:
                # Switch the flag.
                # pylint: disable=modified-iterating-dict
                quotes[q] = not quotes[q]
        if any(quotes.values()):
            # Store the index if the quotes have been opened but not closed yet.
            code_block_line_indices.append(i)
    return code_block_line_indices


def extract_version_from_file_name(file_name: str) -> Tuple[int, int]:
    """
    Extract version number from filename_vXX.json file.

    E.g.
    - 'universe_v3.1.json' -> (3, 1)
    - 'universe_v1.json' -> (1, 0)
    - 'dataset_schema_v3.json' -> (3, 0)

    Currently only JSON file extension is supported.

    :param file_name: file to extract version part from
    :return: file version tuple in format (major, minor)
    """
    basename = os.path.basename(file_name).rstrip(".json")
    m = re.search(r"v(\d+(\.\d+)?)$", basename)
    hdbg.dassert(
        m,
        "Can't parse file '%s', correct format is e.g. 'universe_v03.json'.",
        basename,
    )
    # Groups return tuple.
    version = m.groups(1)[0].split(".")  # type: ignore[arg-type, union-attr]
    major, minor = int(version[0]), 0 if len(version) == 1 else int(version[1])
    return major, minor

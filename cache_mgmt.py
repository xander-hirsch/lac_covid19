"""Interfaces with the filesystem to manage a cache of returned values from
    resource intensive tasks.
"""

import os.path
from typing import Any, Callable, Dict, Optional

CACHE_DIR = os.path.join(os.path.dirname(__file__), 'memoization')
BAD_DATA_MSG = 'The contents do not pass the assertion check'


def write_cache(contents: Any, filename: str, is_binary,
                assert_check: Callable, write_func: Callable) -> None:
    """Customizable function to write some file contents to a local
    cache directory.

    Args:
        contents: The data to be written out.
        filename: The filename of the cache file. Do not include a
            directory prefix.
        write_func: A function used to put contents into the file
            output. This takes the contents as the first parameter and
            the I/O object as the second parameter.
        assert_check: A function to check the validity of the output
            data. This takes contents as the only input and returns a
            boolean.
    """

    if not assert_check(contents):
        print('Content type: ', type(contents))
        raise ValueError(BAD_DATA_MSG)

    if not os.path.isdir(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    mode_ = 'w'
    if is_binary:
        mode_ += 'b'

    with open(os.path.join(CACHE_DIR, filename), mode_) as f:
        write_func(contents, f)


def read_cache(filename: str, is_binary: bool, assert_check: Callable,
               read_func: Callable) -> Optional[Any]:
    """Customizable function to read file contents.

    Args:
        filename: The filename of the cache. Do not include a directory
            prefix.
        read_func: A function to read in the file properly. It takes an
            I/O object and returns the containted contents.
        assert_check: A function to ensure the proper data if a read is
            successful. It takes in the read contents as the only
            argument and outputs a boolean.
    Returns:
        If the file exists, it returns what is returned by read_func when
        passed the target file I/O object. If the file does not exist,
        it returns None.
    """

    file_ = os.path.join(CACHE_DIR, filename)
    mode_ = 'r'
    if is_binary:
        mode_ += 'b'

    if os.path.isfile(file_):
        with open(file_, mode_) as f:
            output = read_func(f)

            if not assert_check(output):
                raise ValueError(BAD_DATA_MSG)

            return output
    else:
        return None


def use_cache(
        filename: str, is_binary: bool, assert_check: Callable,
        read_func: Callable, write_func: Callable,
        fallback_func: Callable, *fallback_args) -> Any:
    """Attempts to read result from cache first before falling back to
        another function."""

    cached_val = read_cache(filename, is_binary, assert_check, read_func)

    if not cached_val:
        cached_val = fallback_func(*fallback_args)
        write_cache(cached_val, filename, is_binary, assert_check, write_func)

    return cached_val


def is_json_dict(contents: Dict) -> bool:
    return (isinstance(contents, dict) 
            and all(map(lambda x: isinstance(x, str), contents.keys()))
            or isinstance(contents, list))
# coding=utf-8
"""Python old versions compatibility"""
import abc as _abc
import concurrent.futures as _futures
import re as _re
import os as _os
import shutil as _shutil
from sys import version_info as _py

# Python 2 compatibility
if _py[0] == 2:

    # Missing .timestamp() method of "datetime.datetime"
    import time as _time


    def to_timestamp(dt):
        """Return POSIX timestamp as float"""
        return _time.mktime(dt.timetuple()) + dt.microsecond / 1e6


    # Missing "os.fsdecode"
    def fsdecode(filename):
        """Return filename unchanged"""
        return filename

    # Mission "exists_ok" in "os.makedirs"
    def makedirs(name, mode=0o777, exist_ok=False):
        """
        Super-mkdir; create a leaf directory and all intermediate ones.
        Works like mkdir, except that any intermediate path segment
        (not just the rightmost) will be created if it does not exist.

        Args:
            name (str): Path
            mode (int): The mode parameter is passed to os.mkdir();
                see the os.mkdir() description for how it is interpreted.
            exist_ok (bool): Don't raises error if target directory already
                exists.

        Raises:
            OSError: if exist_ok is False and if the target directory already
                exists.
        """
        try:
            _os.makedirs(name, mode)
        except OSError:
            if not exist_ok or not _os.path.isdir(name):
                raise

    # Missing "follow_symlinks" in "copyfile"
    def copyfile(src, dst, follow_symlinks=True):
        """
        Copies a source file to a destination file.

        Args:
            src (str): Source file.
            dst (str): Destination file.
            follow_symlinks (bool): Ignored.
        """
        _shutil.copyfile(src, dst)

    # Missing "abc.ABC"
    ABC = _abc.ABCMeta('ABC', (object,), {})

    # Missing exceptions
    file_not_found_error = OSError
    permission_error = OSError
    file_exits_error = OSError
    same_file_error = OSError
    is_a_directory_error = OSError

else:
    def to_timestamp(dt):
        """Return POSIX timestamp as float"""
        return dt.timestamp()

    fsdecode = _os.fsdecode
    makedirs = _os.makedirs
    copyfile = _shutil.copyfile
    ABC = _abc.ABC
    file_not_found_error = FileNotFoundError
    permission_error = PermissionError
    file_exits_error = FileExistsError
    same_file_error = _shutil.SameFileError
    is_a_directory_error = IsADirectoryError


# Python 2 Windows compatibility
try:
    from os.path import samefile
except ImportError:

    def samefile(*_, **__):
        """Checks if same files."""
        raise NotImplementedError(
            '"os.path.samefile" not available on Windows with Python 2.')


# Python 3.4 compatibility
if _py[0] == 3 and _py[1] == 4:

    # "max_workers" as keyword argument for ThreadPoolExecutor
    class ThreadPoolExecutor(_futures.ThreadPoolExecutor):
        """concurrent.futures.ThreadPoolExecutor"""
        def __init__(self, max_workers=None, **kwargs):
            """Initializes a new ThreadPoolExecutor instance.

            Args:
                max_workers: The maximum number of threads that can be used to
                    execute the given calls.
            """
            if max_workers is None:
                # Use this number because ThreadPoolExecutor is often
                # used to overlap I/O instead of CPU work.
                max_workers = (_os.cpu_count() or 1) * 5
            _futures.ThreadPoolExecutor.__init__(self, max_workers, **kwargs)

else:
    ThreadPoolExecutor = _futures.ThreadPoolExecutor

# Python <= 3.6 compatibility
if _py[0] < 3 or (_py[0] == 3 and _py[1] <= 6):
    # Missing re.Pattern
    Pattern = type(_re.compile(''))

else:
    Pattern = _re.Pattern

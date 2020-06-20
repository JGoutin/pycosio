"""Base utilities to define storage functions"""

from functools import wraps
from os import fsdecode, fsencode

from airfs._core.exceptions import handle_os_exceptions


def is_storage(url, storage=None):
    """
    Check if file is a local file or a storage file.

    File is considered local if:
        - URL is a local path.
        - URL starts by "file://"
        - a "storage" is provided.

    Args:
        url (str): file path or URL
        storage (str): Storage name.

    Returns:
        bool: return True if file is local.
    """
    if storage:
        return True
    split_url = url.split("://", 1)
    if len(split_url) == 2 and split_url[0].lower() != "file":
        return True
    return False


def format_and_is_storage(path):
    """
    Checks if path is storage and format it.

    If path is an opened file-like object, returns is storage as True.

    Args:
        path (path-like object or file-like object):

    Returns:
        tuple: str or file-like object (Updated path),
            bool (True if is storage).
    """
    if not hasattr(path, "read"):
        path = fsdecode(path).replace("\\", "/")
        return path, is_storage(path)
    return path, True


def equivalent_to(std_function, keep_path_type=False):
    """
    Decorates an airfs object compatible function to provides fall back to standard
    function if used on local files.

    Args:
        std_function (function): standard function to use with local files.
        keep_path_type (bool): Convert returned result to bytes if path argument was
            bytes.

    Returns:
        function: new function
    """

    def decorate(cos_function):
        """Decorator argument handler

        Args:
            cos_function (function): Storage function to use with storage files.
        """

        @wraps(cos_function)
        def decorated(path, *args, **kwargs):
            """
            Decorated function.

            Args:
                path (path-like object): Path or URL.
            """

            # Handles path-like objects
            path_str = fsdecode(path).replace("\\", "/")

            # Storage object: Handle with Cloud object storage function
            if is_storage(path_str):
                with handle_os_exceptions():
                    result = cos_function(path_str, *args, **kwargs)
                if keep_path_type and isinstance(path, bytes):
                    result = fsencode(result)
                return result

            # Local file: Redirect to standard function
            return std_function(path, *args, **kwargs)

        return decorated

    return decorate

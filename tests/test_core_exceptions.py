"""Test airfs._core.exceptions"""

import pytest


def test_handle_os_exceptions():
    """Tests airfs._core.exceptions.handle_os_exceptions"""
    from airfs._core.exceptions import (
        handle_os_exceptions,
        ObjectNotFoundError,
        ObjectPermissionError,
        ObjectNotADirectoryError,
        ObjectExistsError,
    )

    with pytest.raises(FileNotFoundError):
        with handle_os_exceptions():
            raise ObjectNotFoundError("error")

    with pytest.raises(PermissionError):
        with handle_os_exceptions():
            raise ObjectPermissionError("error")

    with pytest.raises(FileExistsError):
        with handle_os_exceptions():
            raise ObjectExistsError("error")

    with pytest.raises(NotADirectoryError):
        with handle_os_exceptions():
            raise ObjectNotADirectoryError("error")

    with pytest.raises(FileExistsError):
        with handle_os_exceptions():
            raise FileExistsError()

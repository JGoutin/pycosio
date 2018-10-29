# coding=utf-8
"""Google Cloud Storage"""
from contextlib import contextmanager as _contextmanager

from google.cloud.storage.client import Client as _Client

from pycosio._core.exceptions import (
    ObjectNotFoundError as _ObjectNotFoundError,
    ObjectPermissionError as _ObjectPermissionError)
from pycosio.io import (
    ObjectRawIOBase as _ObjectRawIOBase,
    ObjectBufferedIOBase as _ObjectBufferedIOBase,
    SystemBase as _SystemBase)


@_contextmanager
def _handle_google_exception():
    """
    Handle Google cloud exception and convert to class
    IO exceptions

    Raises:
        OSError subclasses: IO error.
    """
    yield
    # TODO:


class _GSSystem(_SystemBase):
    """
    Google Cloud Storage system.

    Args:
        storage_parameters (dict): ????
        unsecure (bool): If True, disables TLS/SSL to improves
            transfer performance. But makes connection unsecure.
    """
    _CTIME_KEYS = ('timeCreated',)
    _MTIME_KEYS = ('updated',)
    _SIZE_KEYS = ('size',)

    def copy(self, src, dst):
        """
        Copy object of the same storage.

        Args:
            src (str): Path or URL.
            dst (str): Path or URL.
        """
        dst_client_kwargs = self.get_client_kwargs(dst)
        with _handle_google_exception():
            self.client.copy_blob(
                blob=self._get_blob(self.get_client_kwargs(src)),
                destination_bucket=self._get_bucket(dst_client_kwargs),
                new_name=dst_client_kwargs['blob_name'])

    def _get_blob(self, client_kwargs):
        """
        Get blob object.

        Returns:
            google.cloud.storage.blob.Blob: Blob object
        """
        return self._get_bucket(client_kwargs).get_blob(
            blob_name=client_kwargs['blob_name'])

    def _get_client(self):
        """
        Google storage client

        Returns:
            google.cloud.storage.client.Client: client
        """
        return _Client(**self._storage_parameters)

    def get_client_kwargs(self, path):
        """
        Get base keyword arguments for client for a
        specific path.

        Args:
            path (str): Absolute path or URL.

        Returns:
            dict: client args
        """
        bucket_name, key = self.split_locator(path)
        kwargs = dict(bucket_name=bucket_name)
        if key:
            kwargs['blob_name'] = key
        return kwargs

    def _get_bucket(self, client_kwargs):
        """
        Get bucket object.

        Returns:
            google.cloud.storage.bucket.Bucket: Bucket object
        """
        return self.client.get_bucket(bucket_name=client_kwargs['bucket_name'])

    def _get_roots(self):
        """
        Return URL roots for this storage.

        Returns:
            tuple of str or re.Pattern: URL roots
        """
        return (
                # "gs" URL scheme
                'gs://',)
                # TODO: HTTPS URL roots

    def _head(self, client_kwargs):
        """
        Returns object or bucket HTTP header.

        Args:
            client_kwargs (dict): Client arguments.

        Returns:
            dict: HTTP header.
        """
        with _handle_google_exception():
            # Object
            if 'blob_name' in client_kwargs:
                obj = self._get_blob(client_kwargs)

            # Bucket
            else:
                obj = self._get_bucket(client_kwargs)

        return obj._properties

    def _list_locators(self):
        """
        Lists locators.

        Returns:
            generator of tuple: locator name str, locator header dict
        """
        with _handle_google_exception():
            buckets = self.client.list_buckets()

        for bucket in buckets:
            # TODO:
            yield bucket.name, bucket._properties

    def _list_objects(self, client_kwargs, path, max_request_entries):
        """
        Lists objects.

        args:
            client_kwargs (dict): Client arguments.
            path (str): Path relative to current locator.
            max_request_entries (int): If specified, maximum entries returned
                by request.

        Returns:
            generator of tuple: object name str, object header dict
        """
        client_kwargs = client_kwargs.copy()
        if max_request_entries:
            client_kwargs['max_results'] = max_request_entries

        with _handle_google_exception():
            bucket = self._get_bucket(client_kwargs)

        while True:
            with _handle_google_exception():
                blobs = bucket.list_blobs(prefix=path, **client_kwargs)

            for blob in blobs:
                yield blob.name, blob._properties
            # TODO: next pages

    def _make_dir(self, client_kwargs):
        """
        Make a directory.

        args:
            client_kwargs (dict): Client arguments.
        """
        with _handle_google_exception():
            # Object
            # TODO:

            # Bucket
            return self.client.create_bucket(
                bucket_name=client_kwargs['bucket_name'])

    def _remove(self, client_kwargs):
        """
        Remove an object.

        args:
            client_kwargs (dict): Client arguments.
        """
        with _handle_google_exception():
            # Object
            if 'blob_name' in client_kwargs:
                self._get_bucket(client_kwargs).delete_blob(
                    blob_name=client_kwargs['blob_name'])

            # Bucket
            return self._get_bucket(client_kwargs).delete()


class GSRawIO(_ObjectRawIOBase):
    """Binary Google Cloud Storage Object I/O

    Args:
        name (path-like object): URL or path to the file which will be opened.
        mode (str): The mode can be 'r', 'w', 'a'
            for reading (default), writing or appending
        storage_parameters (dict): ????
        unsecure (bool): If True, disables TLS/SSL to improves
            transfer performance. But makes connection unsecure.
    """
    _SYSTEM_CLASS = _GSSystem

    def _read_range(self, start, end=0):
        """
        Read a range of bytes in stream.

        Args:
            start (int): Start stream position.
            end (int): End stream position.
                0 To not specify end.

        Returns:
            bytes: number of bytes read
        """
        # TODO:

    def _readall(self):
        """
        Read and return all the bytes from the stream until EOF.

        Returns:
            bytes: Object content
        """
        # TODO:

    def _flush(self):
        """
        Flush the write buffers of the stream if applicable.
        """
        # TODO:


class GSBufferedIO(_ObjectBufferedIOBase):
    """Buffered binary Google Cloud Storage Object I/O

    Args:
        name (path-like object): URL or path to the file which will be opened.
        mode (str): The mode can be 'r', 'w' for reading (default) or writing
        buffer_size (int): The size of buffer.
        max_buffers (int): The maximum number of buffers to preload in read mode
            or awaiting flush in write mode. 0 for no limit.
        max_workers (int): The maximum number of threads that can be used to
            execute the given calls.
        storage_parameters (dict): ????
        unsecure (bool): If True, disables TLS/SSL to improves
            transfer performance. But makes connection unsecure.
    """
    _RAW_CLASS = GSRawIO

    def _flush(self):
        """
        Flush the write buffers of the stream.
        """
        # TODO:

    def _close_writable(self):
        """
        Close the object in write mode.
        """
        # TODO:

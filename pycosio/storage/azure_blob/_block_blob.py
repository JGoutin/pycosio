# coding=utf-8
"""Microsoft Azure Blobs Storage"""
from __future__ import absolute_import  # Python 2: Fix azure import

from random import choice
from string import ascii_lowercase as _ascii_lowercase

from azure.storage.blob import BlobBlock
from azure.storage.blob.models import _BlobTypes

from pycosio.storage.azure import _handle_azure_exception
from pycosio._core.io_base import memoizedmethod
from pycosio.io import ObjectBufferedIOBase
from pycosio.storage.azure_blob._base_blob import (
    AzureBlobRawIO, AzureBlobBufferedIO, AZURE_RAW, AZURE_BUFFERED)

_BLOB_TYPE = _BlobTypes.BlockBlob


class AzureBlockBlobRawIO(AzureBlobRawIO):
    """Binary Azure BLock Blobs Storage Object I/O

    Args:
        name (path-like object): URL or path to the file which will be opened.
        mode (str): The mode can be 'r', 'w', 'a'
            for reading (default), writing or appending
        storage_parameters (dict): Azure service keyword arguments.
            This is generally Azure credentials and configuration. See
            "azure.storage.blob.baseblobservice.BaseBlobService" for more
            information.
        unsecure (bool): If True, disables TLS/SSL to improves
            transfer performance. But makes connection unsecure.
    """
    _SUPPORT_PART_FLUSH = False
    _DEFAULT_CLASS = False

    def __init__(self, *args, **kwargs):
        AzureBlobRawIO.__init__(self, *args, **kwargs)

        # Creates blob on write mode
        if self._is_new_file:
            with _handle_azure_exception():
                self._client.create_blob_from_bytes(
                    blob=b'', **self._client_kwargs)

    @property
    @memoizedmethod
    def _client(self):
        """
        Returns client instance.

        Returns:
            azure.storage.blob.pageblobservice.PageBlobService: client
        """
        return self._system.client[_BLOB_TYPE]

    def _flush(self, buffer, start, end):
        """
        Flush the write buffer of the stream if applicable.

        Args:
            buffer (memoryview): Buffer content.
            start (int): Start of buffer position to flush.
                Supported only with page blobs.
            end (int): End of buffer position to flush.
                Supported only with page blobs.
        """
        with _handle_azure_exception():
            # Write entire file at once
            self._client.create_blob_from_bytes(
                blob=buffer.tobytes(), **self._client_kwargs)


class AzureBlockBlobBufferedIO(AzureBlobBufferedIO):
    """Buffered binary Azure Block Blobs Storage Object I/O

    Args:
        name (path-like object): URL or path to the file which will be opened.
        mode (str): The mode can be 'r', 'w' for reading (default) or writing
        buffer_size (int): The size of buffer.
        max_buffers (int): The maximum number of buffers to preload in read mode
            or awaiting flush in write mode. 0 for no limit.
        max_workers (int): The maximum number of threads that can be used to
            execute the given calls.
        storage_parameters (dict): Azure service keyword arguments.
            This is generally Azure credentials and configuration. See
            "azure.storage.blob.baseblobservice.BaseBlobService" for more
            information.
        unsecure (bool): If True, disables TLS/SSL to improves
            transfer performance. But makes connection unsecure.
    """
    _RAW_CLASS = AzureBlockBlobRawIO
    _DEFAULT_CLASS = False

    def __init__(self, *args, **kwargs):
        ObjectBufferedIOBase.__init__(self, *args, **kwargs)
        if self._writable:
            self._blocks = []

    @staticmethod
    def _get_random_block_id(length):
        """
        Generate a random ID.

        Args:
            length (int): ID length.

        Returns:
            str: Random block ID.
        """
        return ''.join(choice(_ascii_lowercase) for _ in range(length))

    def _flush(self):
        """
        Flush the write buffer of the stream.
        """
        block_id = self._get_random_block_id(32)

        # Upload block with workers
        self._write_futures.append(self._workers.submit(
            self._client.put_block, block=self._get_buffer().tobytes(),
            block_id=block_id, **self._client_kwargs))

        # Save block information
        self._blocks.append(BlobBlock(id=block_id))

    def _close_writable(self):
        """
        Close the object in write mode.
        """
        for future in self._write_futures:
            future.result()

        block_list = self._client.get_block_list(**self._client_kwargs)
        self._client.put_block_list(
            block_list=block_list.committed_blocks + self._blocks,
            **self._client_kwargs)


AZURE_RAW[_BLOB_TYPE] = AzureBlockBlobRawIO
AZURE_BUFFERED[_BLOB_TYPE] = AzureBlockBlobBufferedIO

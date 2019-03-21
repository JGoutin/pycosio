# coding=utf-8
"""Test pycosio.storage.azure_file"""
from __future__ import absolute_import  # Python 2: Fix azure import

UNSUPPORTED_OPERATIONS = (
    'symlink',

    # Not supported on some objects
    'getctime',
)


def test_mocked_storage():
    """Tests pycosio.azure_file with a mock"""
    from azure.storage.file.models import (
        Share, File, Directory, ShareProperties, FileProperties,
        DirectoryProperties)

    import pycosio.storage.azure_file as azure_file
    from pycosio.storage.azure_file import (
        AzureFileRawIO, _AzureFileSystem, AzureFileBufferedIO)

    from tests.test_storage import StorageTester
    from tests.test_storage_azure import get_storage_mock

    # Mocks client
    storage_mock = get_storage_mock()
    root = '//account.file.core.windows.net'

    def join(directory_name=None, file_name=None):
        """
        Join paths elements

        Args:
            directory_name (str): Directory.
            file_name (str): File.

        Returns:
            str: Path
        """
        if directory_name and file_name:
            return '%s/%s' % (directory_name, file_name)
        elif directory_name:
            return directory_name
        return file_name

    class FileService:
        """azure.storage.file.fileservice.FileService"""

        def __init__(self, *_, **__):
            """azure.storage.file.fileservice.FileService.__init__"""

        @staticmethod
        def copy_file(share_name=None, directory_name=None, file_name=None,
                      copy_source=None, **_):
            """azure.storage.file.fileservice.FileService.copy_file"""
            copy_source = copy_source.split(root + '/')[1]
            storage_mock.copy_object(
                src_path=copy_source, dst_locator=share_name,
                dst_path=join(directory_name, file_name))

        @staticmethod
        def get_file_properties(
                share_name=None, directory_name=None, file_name=None, **_):
            """azure.storage.file.fileservice.FileService.get_file_properties"""
            args = share_name, join(directory_name, file_name)
            props = FileProperties()
            props.last_modified = storage_mock.get_object_mtime(*args)
            props.content_length = storage_mock.get_object_size(*args)
            return File(props=props, name=file_name)

        @staticmethod
        def get_directory_properties(share_name=None, directory_name=None, **_):
            """
            azure.storage.file.fileservice.FileService.get_directory_properties
            """
            props = DirectoryProperties()
            props.last_modified = storage_mock.get_object_mtime(
                share_name, directory_name)
            return Directory(props=props, name=directory_name)

        @staticmethod
        def get_share_properties(share_name=None, **_):
            """
            azure.storage.file.fileservice.FileService.get_share_properties
            """
            props = ShareProperties()
            props.last_modified = storage_mock.get_locator_mtime(share_name)
            return Share(props=props, name=share_name)

        @staticmethod
        def list_shares():
            """azure.storage.file.fileservice.FileService.list_shares"""
            shares = []
            for share_name in storage_mock.get_locators():
                props = ShareProperties()
                props.last_modified = storage_mock.get_locator_mtime(share_name)
                shares.append(Share(props=props, name=share_name))
            return shares

        @staticmethod
        def list_directories_and_files(
                share_name=None, directory_name=None, prefix=None,
                num_results=None, **_):
            """
            azure.storage.file.fileservice.FileService.
            list_directories_and_files
            """
            files = []
            for file_name in storage_mock.get_locator(
                    share_name, prefix=prefix, limit=num_results):
                props = FileProperties()
                props.last_modified = storage_mock.get_object_mtime(
                    share_name, file_name)
                props.content_length = storage_mock.get_object_size(
                    share_name, file_name)
                files.append(File(props=props, name=file_name))
            return files

        @staticmethod
        def create_directory(share_name=None, directory_name=None, **_):
            """azure.storage.file.fileservice.FileService.create_directory"""
            storage_mock.put_object(share_name, directory_name + '/')

        @staticmethod
        def create_share(share_name=None, **_):
            """azure.storage.file.fileservice.FileService.create_share"""
            storage_mock.put_locator(share_name)

        @staticmethod
        def create_file(share_name=None, directory_name=None,
                        file_name=None, **_):
            """azure.storage.file.fileservice.FileService.create_file"""
            storage_mock.put_object(share_name, join(directory_name, file_name))

        @staticmethod
        def delete_directory(share_name=None, directory_name=None, **_):
            """azure.storage.file.fileservice.FileService.delete_directory"""
            storage_mock.delete_object(share_name, directory_name)

        @staticmethod
        def delete_share(share_name=None, **_):
            """azure.storage.file.fileservice.FileService.delete_share"""
            storage_mock.delete_locator(share_name)

        @staticmethod
        def delete_file(share_name=None, directory_name=None,
                        file_name=None, **_):
            """azure.storage.file.fileservice.FileService.delete_file"""
            storage_mock.delete_object(
                share_name, join(directory_name, file_name))

        @staticmethod
        def get_file_to_stream(
                share_name=None, directory_name=None, file_name=None,
                stream=None, start_range=None, end_range=None, **_):
            """azure.storage.file.fileservice.FileService.get_file_to_stream"""
            stream.write(storage_mock.get_object(
                share_name, join(directory_name, file_name),
                data_range=(start_range, end_range)))

        @staticmethod
        def update_range(share_name=None, directory_name=None, file_name=None,
                         data=None, start_range=None, end_range=None, **_):
            """azure.storage.file.fileservice.FileService.update_range"""
            storage_mock.put_object(
                share_name, join(directory_name, file_name), content=data,
                data_range=(start_range, end_range))

    azure_storage_file_file_service = azure_file._FileService
    azure_file._FileService = FileService

    # Tests
    try:
        # Init mocked system
        system_parameters = dict(
            storage_parameters=dict(account_name='account'))
        system = _AzureFileSystem(**system_parameters)
        storage_mock.attach_io_system(system)

        # Tests
        with StorageTester(
                system, AzureFileRawIO, AzureFileBufferedIO, storage_mock,
                unsupported_operations=UNSUPPORTED_OPERATIONS,
                system_parameters=system_parameters, root=root) as tester:

            # Common tests
            tester.test_common()

    # Restore mocked class
    finally:
        azure_file._FileService = azure_storage_file_file_service
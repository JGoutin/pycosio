![Tests](https://github.com/JGoutin/airfs/workflows/tests/badge.svg)
[![codecov](https://codecov.io/gh/JGoutin/airfs/branch/master/graph/badge.svg)](https://codecov.io/gh/JGoutin/airfs)
[![Documentation Status](https://readthedocs.org/projects/airfs/badge/?version=latest)](https://airfs.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/airfs.svg)](https://pypi.org/project/airfs)

airfs: A Python library for cloud and remote file Systems
=========================================================

airfs brings standard Python I/O to various storage (like cloud objects storage, remote
file-systems, ...) by providing:

* Abstract classes of Cloud objects with the complete ``io.RawIOBase`` and
  ``io.BufferedIOBase`` standard interfaces.
* Features equivalent to the standard library (``io``, ``os``, ``os.path``, ``shutil``)
  for seamlessly managing storage objects and local files.

These functions are source agnostic and always provide the same interface for all files
from storage or local file systems.

Buffered storage objects also support the following features:

* Buffered asynchronous writing of any object size.
* Buffered asynchronous preloading in reading mode.
* Write or read lock depending on memory usage limitation.
* Maximization of bandwidth using parallels connections.

For more information, refer to the [documentation](https://airfs.readthedocs.io).

Supported storage
-----------------

airfs is compatible with the following storage services:

* Alibaba Cloud OSS
* Amazon Web Services S3 (and compatible)
* GitHub (Read Only)
* Microsoft Azure Blobs Storage
* Microsoft Azure Files Storage
* OpenStack Swift / Object Store

airfs can also access any publicly accessible file via HTTP/HTTPS (Read only).

About airfs and Pycosio
-----------------------

"airfs" is a fork of the Accelize's 
"[Pycosio](https://github.com/Accelize/pycosio)" project.

The "Pycosio" project was started in 2018 to complement the products of the Accelize 
company. Over time and as Accelize products evolved, the library was no longer needed in
the company's products and was maintained less and less. Since mid 2019, Accelize no
longer has an interest in continuing to develop the library and no one is working on it.

As creator and sole developer of the library at Accelize, I decided to create a fork of
the project so that it is now maintained by the open source community under the name
"airfs" (the name "Pycosio" being the property of Accelize).

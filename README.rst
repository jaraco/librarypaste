.. image:: https://img.shields.io/pypi/v/librarypaste.svg
   :target: `PyPI link`_

.. image:: https://img.shields.io/pypi/pyversions/librarypaste.svg
   :target: `PyPI link`_

.. _PyPI link: https://pypi.org/project/librarypaste

.. image:: https://github.com/jaraco/librarypaste/workflows/Automated%20Tests/badge.svg
   :target: https://github.com/jaraco/librarypaste/actions?query=workflow%3A%22Automated+Tests%22
   :alt: Automated Tests

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: Black

.. .. image:: https://readthedocs.org/projects/skeleton/badge/?version=latest
..    :target: https://skeleton.readthedocs.io/en/latest/?badge=latest

Usage
=====

Launch with the ``librarypaste``
command or with ``python -m librarypaste``. The library will host the service
on ``[::0]:8080`` by default. Pass cherrypy config files on the command line
to customize behaivor.

By default, the server saves pastes to the file system  in ``./repo`` using the
JSON store, but there is support for a MongoDB backend as well.

See also `lpaste <https://pypi.org/project/lpaste>`_ for a Python-based
client (including a clipboard helper) and Mac OS X App.

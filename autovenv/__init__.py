"""
autovenv
~~~~~~~~

Autovenv helps you manage your virtual environments.

"""

from __future__ import absolute_import, division, print_function, unicode_literals

from .virtualenvs import VirtualEnvs, get_likely_projfolder, DEFAULT_CONFIG
from .util import create_symlink, mkdir_p, file_exists, resolve_path  # noqa

from .command import do_command

__all__ = [
    "VirtualEnvs",
    "DEFAULT_CONFIG",
    "do_command",
    "get_likely_projfolder",
    "create_symlink",
    "mkdir_p",
]

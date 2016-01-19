"""
autovenv
~~~~~~~~

Autovenv helps you manage your virtual environments.

"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .virtualenvs import VirtualEnvs, get_likely_projfolder


def do_command():
    """Entry point for the 'autovenv' command.

    Simply creates a VirtualEnvs object with default parameters,
    and runs the command via that.
    """

    v = VirtualEnvs()
    v.do_command()


__all__ = ['VirtualEnvs', 'do_command', 'get_likely_projfolder']

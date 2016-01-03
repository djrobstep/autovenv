"""
autovenv
~~~~~~~~

Autovenv helps you manage your virtual environments.

"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse

import os
import sys
import errno

import subprocess
import shutil

from pkg_resources import resource_filename

HOME = os.path.expanduser('~')
CWD = os.getcwd()
PYTHONBUILDS = os.path.expanduser('~/.python-versions')


RECREATE_ERROR = "AUTOVENV: ERROR. Doesn't look like we're in a python" + \
                    "project here (can't find a requirements.txt file)"""


def symlink_force(target, link_name):
    try:
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e


def mkdir_p(path):  # pragma: no cover
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def is_project_root(path):
    return os.path.isfile(os.path.join(path, 'requirements.txt'))


def get_likely_projfolder(fpath, home):
    f = fpath
    likely_projfolder = None

    while True:
        if not f.startswith(home):
            break

        if is_project_root(f):
            likely_projfolder = f

        parent = os.path.dirname(f)
        if parent == f:
            break

        f = parent
    return likely_projfolder


class VirtualEnvs(object):
    """
    This is where the action happens.
    """

    def __init__(self, venv_home=None, home=None, cwd=None, pythonbuilds=None):
        self.home = os.path.abspath(home or HOME)
        self.cwd = os.path.abspath(cwd or CWD)
        self.pythonbuilds = os.path.abspath(pythonbuilds or PYTHONBUILDS)

        if venv_home:
            self.venv_home = os.path.abspath(os.path.expanduser(venv_home))
        else:
            self.venv_home = os.path.expanduser('~/.virtualenvs')

        mkdir_p(self.venv_home)

    def venv_path(self, name):
        return os.path.join(self.venv_home, self.current_pythonbuild_name or
                            '', name)

    @property
    def current_venv_path(self):
        return os.environ.get('VIRTUAL_ENV') or ''

    @property
    def current_venv_python_path(self):
        if self.current_venv_path:
            return os.path.join(self.current_venv_path, 'bin/python')

    @property
    def current_venv_name(self):
        return os.path.split(self.current_venv_path)[1]

    @property
    def likely_projfolder(self):
        return get_likely_projfolder(self.cwd, self.home)

    @property
    def correct_venv_name(self):
        likely = self.likely_projfolder
        return os.path.split(likely or '')[1]

    @property
    def correct_venv_path(self):
        return self.venv_path(self.correct_venv_name)

    def venv_exists(self, name):
        return os.path.exists(self.venv_path(name))

    def activate_path(self, name):
        return os.path.join(self.venv_path(name), 'bin/activate')

    def pip_path(self, name):
        return os.path.join(self.venv_path(name), 'bin/pip')

    def make_virtualenv(self, name):
        new_path = self.venv_path(name)
        if not os.path.isdir(new_path):
            subprocess.call(['virtualenv', new_path])
        else:
            print('PROBLEM: A virtualenv already exists at', new_path)

    def delete_virtualenv(self, name):
        path = self.venv_path(name)
        print('DELETING VIRTUALENV:', path)
        shutil.rmtree(path)

    @property
    def venv_active(self):
        return not not self.current_venv_path

    @property
    def correct_venv_active(self):
        return self.current_venv_path == self.correct_venv_path

    @property
    def pythonbuilds_current(self):
        return os.path.join(self.pythonbuilds, 'current')

    @property
    def pythonbuild_python_path(self):
        return os.path.join(self.pythonbuilds_current, 'bin/python')

    @property
    def pythonbuild_pyvenv_path(self):
        return os.path.join(self.pythonbuilds_current, 'bin/pyvenv')

    @property
    def virtualenv_creation_prefix(self):
        if os.path.exists(self.pythonbuild_pyvenv_path):
            return self.pythonbuild_pyvenv_path
        elif os.path.exists(self.pythonbuild_python_path):
            return 'virtualenv -p {}'.format(self.pythonbuild_python_path)
        else:
            return 'virtualenv'

    @property
    def current_pythonbuild_name(self):
        if os.path.exists(self.pythonbuilds_current):
            realpath = os.path.realpath(self.pythonbuilds_current)
            return os.path.split(realpath)[1]

    @property
    def suggested_bash_command(self):
        """Generates the correct bash command to make sure that the appropriate
        virtualenv is activated for the project folder you're in (or to
        deactivate if you're not in a project folder.)
        """
        wanted = self.correct_venv_name

        if wanted:
            command = ''

            if not self.venv_exists(wanted):
                s = "echo 'AUTOVENV: creating virtual environment: {}'; "
                command += s.format(wanted)

                s = "{} {}; "
                command += s.format(self.virtualenv_creation_prefix,
                                    self.correct_venv_path)

            if not self.correct_venv_active:
                command += '. {0}; '.format(self.activate_path(
                    self.correct_venv_name))

            if command:
                return 'eval {}'.format(command)

        elif self.current_venv_name:
            return "eval echo 'AUTOVENV: deactivating...' ; deactivate"

        return ''

    def recreate(self):
        if self.venv_active:
            self.delete_virtualenv(self.correct_venv_name)
            self.make_virtualenv(self.correct_venv_name)
        else:
            print(RECREATE_ERROR)

    @property
    def build_defs_path(self):
        return resource_filename(__name__, 'python-build/share/python-build')

    def do_command(self):

        parser = argparse.ArgumentParser(
            description='Work with venvs and python versions.')
        parser.set_defaults(info=False,
                            bash=False,
                            python_version=False,
                            recreate=False,
                            builddefspath=False)
        subparsers = parser.add_subparsers()

        bash = subparsers.add_parser(
            'bash',
            help='suggests a bash command that'
            ' (hopefully) will activate the correct venv for this project')
        bash.set_defaults(bash=True)
        recreate = subparsers.add_parser('recreate',
                                         help='wipe the current virtualenv'
                                         ' and reinstall it from scratch')
        recreate.set_defaults(recreate=True)
        info = subparsers.add_parser('info',
                                     help='show the current virtual'
                                     ' environment and python version in use')
        info.set_defaults(info=True)
        builddefspath = subparsers.add_parser(
            'builddefspath',
            help='show the current virtual'
            ' environment and python version in use')
        builddefspath.set_defaults(builddefspath=True)

        choose = subparsers.add_parser(
            'choose',
            help='set your preferred python version')
        choose.add_argument(
            'python_version',
            help='your preferred python version '
            '(see possible versions with "autovenv-pythons-available")')

        if not sys.argv[1:]:
            parser.print_help()
            return
        else:
            args = parser.parse_args()

        if args.bash:
            print(self.suggested_bash_command)
        elif args.recreate:
            self.recreate()
        elif args.info:
            if self.current_venv_path:
                print('Using this virtualenv: {}'.format(
                    self.current_venv_path))
            else:
                print('Using system environment')
            if self.current_venv_python_path:
                p = self.current_venv_python_path
                print('Using this python: {}'.format(p))
                print('...which is really at: {}'.format(os.path.realpath(p)))
            else:
                print('Using system python')
        elif args.builddefspath:
            print(self.build_defs_path)
        elif args.python_version:
            target = os.path.join(self.pythonbuilds, args.python_version)
            rel_target = os.path.relpath(target, self.pythonbuilds)
            link_name = self.pythonbuilds_current
            symlink_force(rel_target, link_name)
            print('Now using the python at: {}'.format(target))


def do_command():
    """Entry point for the 'autovenv' command.

    Simply creates a VirtualEnvs object with default parameters,
    and runs the command via that.
    """

    v = VirtualEnvs()
    v.do_command()

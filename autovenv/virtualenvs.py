from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse

import os
import sys
import io
import errno

import subprocess
import shutil
import shlex

from pkg_resources import resource_filename

HOME = os.path.expanduser('~')
CWD = os.getcwd()
PYTHONBUILDS = os.path.expanduser('~/.python-versions')

RECREATE_ERROR = "AUTOVENV: ERROR (not within a python project)"


def symlink_force(target, link_name):
    """
    Creates a symlink. If a symlink of this link name
    already exists, replace it.
    """

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
    """Tests if a given folder path is likely to be the
    root of a python project. At the moment, this simply tests
    for the presence of a requirements.txt file.
    """
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
        """Returns the path of the currently active
        virtual environment.
        """

        return os.environ.get('VIRTUAL_ENV') or ''

    @property
    def current_venv_python_path(self):
        """If a virtual environment is activated, return the
        path to the python executable. Otherwise, return None.
        """
        if self.current_venv_path:
            return os.path.join(self.current_venv_path, 'bin/python')

    @property
    def current_venv_name(self):
        """If a virtual environment is activated, return
        that virtual environment's (folder) name.

        Otherwise, return an empty string.
        """
        return os.path.split(self.current_venv_path)[1]

    @property
    def likely_projfolder(self):
        """If we're within a python project, return the
        path to the root of that project. Otherwise, return None.
        """
        return get_likely_projfolder(self.cwd, self.home)

    @property
    def correct_venv_name(self):
        """Returns the name of the virtualenvironment that
        should be active for this project. If we're not within
        a project, return an empty string.
        """

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
        """Make a new virtual environment with the given name.

        """
        new_path = self.venv_path(name)

        tokens = shlex.split(self.virtualenv_creation_prefix)
        tokens.append(new_path)

        if not os.path.isdir(new_path):
            subprocess.call(tokens)
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
    def pythonversion_path(self):
        if self.current_pythonbuild_name:
            return os.path.join(self.pythonbuilds,
                                self.current_pythonbuild_name)

    @property
    def python_path(self):
        p = self.pythonversion_path
        if p:
            return os.path.join(p, 'bin/python')
        else:
            return sys.executable

    @property
    def pyvenv_path(self):
        p = self.pythonversion_path
        if p:
            return os.path.join(p, 'bin/pyvenv')
        else:
            return ''

    @property
    def virtualenv_creation_prefix(self):
        p_pyvenv = self.pyvenv_path
        p_python = self.python_path

        if os.path.exists(p_pyvenv):
            return p_pyvenv
        elif os.path.exists(p_python):
            return 'virtualenv -p {}'.format(p_python)

        raise ValueError('something went wrong finding a python')

    @property
    def pythonversion_file_path(self):
        projfolder = self.likely_projfolder
        if projfolder:
            return os.path.join(projfolder, '.python-version')
        else:
            return ''

    @property
    def current_pythonbuild_name(self):
        """Gets the name of the non-system python to use.
        This is the version specified in the .python-version
        file in the project root (if it exists), or else
        the version set with "autovenv choose (name)".

        If neither of these two conditions apply, this will
        return None, and so the system python will be used.
        """

        if os.path.exists(self.pythonversion_file_path):
            with io.open(self.pythonversion_file_path) as f:
                version_string = f.read().strip()
                if version_string:
                    return version_string

        if os.path.exists(self.pythonbuilds_current):
            realpath = os.path.realpath(self.pythonbuilds_current)
            return os.path.split(realpath)[1]

    @property
    def suggested_bash_command(self):
        """Generates the correct bash command to make sure that the
        appropriate virtualenv is activated for the project folder
        you're in (or to deactivate if you're not in a project folder).
        """
        wanted = self.correct_venv_name

        if wanted:
            command = ''

            if not os.path.exists(self.correct_venv_path):
                s = "echo 'AUTOVENV: creating virtual environment: {}{}'; "

                if self.current_pythonbuild_name:
                    version_info = \
                        " (using non-system python version {})"\
                        .format(self.current_pythonbuild_name)
                else:
                    version_info = ''

                command += s.format(wanted, version_info)

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
            help='returns the path where'
            'the python-build definitions are stored')
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

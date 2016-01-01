"""
autovenv
~~~~~~~~

Autovenv helps you manage your virtual environments.

"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse

import os
import errno

import subprocess
import shutil

HOME = os.path.expanduser('~')
CWD = os.getcwd()

RECREATE_ERROR = "AUTOVENV: ERROR. Doesn't look like we're in a python" + \
                    "project here (can't find a requirements.txt file)"""


COMMAND_HELP = \
    '"autovenv bash" suggests a bash command that (hopefully) ' + \
    ' will activate the correct virtualenv for this project. ' + \
    '"autovenv recreate" will wipe the current virtualenv and ' + \
    'reinstall it from scratch'


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

    def __init__(self, venv_home=None, home=None, cwd=None):
        self.home = os.path.abspath(home or HOME)
        self.cwd = os.path.abspath(cwd or CWD)

        if venv_home:
            self.venv_home = os.path.abspath(os.path.expanduser(venv_home))
        else:
            self.venv_home = os.path.expanduser('~/.virtualenvs')

        mkdir_p(self.venv_home)

    def venv_path(self, name):
        return os.path.join(self.venv_home, name)

    @property
    def current_venv_path(self):
        return os.environ.get('VIRTUAL_ENV') or ''

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
        return self.current_venv_name == self.correct_venv_name

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

                s = "virtualenv {}; {} install --upgrade pip; "
                command += s.format(self.correct_venv_path,
                                    self.pip_path(wanted))

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

    def do_command(self):
        parser = argparse.ArgumentParser(description='Work with venvs.')
        parser.add_argument('action', metavar='action', help=COMMAND_HELP)

        args = parser.parse_args()

        if args.action == 'bash':
            print(self.suggested_bash_command)
        elif args.action == 'recreate':
            self.recreate()
        else:
            return parser.error('uncognized command: "{}"'.format(args.action))


def do_command():
    """Entry point for the 'autovenv' command.

    Simply creates a VirtualEnvs object with default parameters,
    and runs the command via that.
    """

    v = VirtualEnvs()
    v.do_command()

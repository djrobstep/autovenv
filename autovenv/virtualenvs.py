from __future__ import absolute_import, division, print_function, unicode_literals

from pathlib2 import Path

import os
import sys
import io
import errno

import subprocess
import shutil
import shlex

from pkg_resources import resource_filename

import appdirs

import yaml

from .util import (
    mkdir_p,
    create_symlink,
    resolve_path,
    resolve_path_pathlib,
    jsondump,
    to_string,
    unresolve,
    shquote,
)


HOME = os.path.expanduser("~")
CWD = os.getcwd()

dirs = appdirs.AppDirs("autovenv", "djrobstep")

DATA_DIR = dirs.user_data_dir

RECREATE_ERROR = "AUTOVENV: ERROR (not within a python project)"


def is_project_root(path, file_names=None):
    """Tests if a given folder path is likely to be the
    root of a python project.
    """

    def file_is_present(filename):
        return os.path.isfile(os.path.join(path, filename))

    file_names = file_names or []
    return any(file_is_present(each) for each in file_names)


def get_likely_projfolder(fpath, home, config=None):
    config = config or {}

    if config:
        overrides = config.get("overrides", {})
        for k, v in overrides:
            if not v["venvname"]:
                continue
            if fpath.startswith(k):
                return k

    f = fpath
    likely_projfolder = None

    while True:
        if not f.startswith(home):
            break

        if is_project_root(f, config.get("file_names")):
            likely_projfolder = f

        parent = os.path.dirname(f)
        if parent == f:
            break

        f = parent

    if likely_projfolder:
        return likely_projfolder


DEFAULT_CONFIG = {"file_names": ["requirements.txt"]}


def parse_override(v):
    if not v:
        pyversion = None
        venvname = None
    else:
        try:
            pyversion, venvname = v.split("/", 1)
            pyversion = pyversion or None
            venvname = venvname or None
        except ValueError:
            pyversion = v
            venvname = None
    return dict(pyversion=pyversion, venvname=venvname)


def unparse_override(v):
    pyversion = v["pyversion"]
    venvname = v["venvname"]
    s = pyversion or ""
    if venvname:
        s += "/{}".format(venvname)
    return s or None


class VirtualEnvs(object):
    """
    This is where the action happens.
    """

    def __init__(self, data_dir=None, home=None, cwd=None):
        self.data_dir = resolve_path(data_dir or DATA_DIR)
        self.home = resolve_path(home or HOME)
        self.cwd_pathlib = resolve_path_pathlib(cwd or CWD)
        self.cwd = str(self.cwd_pathlib)

        self.configpath = os.path.join(self.data_dir, "config")

        if self.should_use_framework_build:
            pvname = "pyversions-framework"
        else:
            pvname = "pyversions"

        if sys.platform == "darwin":
            pvname = "." + pvname

            self.pyversionspath = os.path.join(self.home, pvname)
            self.venvspath = os.path.join(self.home, ".autovenv")

        else:
            self.pyversionspath = os.path.join(self.data_dir, pvname)
            self.venvspath = os.path.join(self.data_dir, "venvs")
        mkdir_p(self.venvspath)

        self.pyversionspath_framework = self.pyversionspath.replace(
            "pyversions", "pyversions-framework"
        )

        self.config = self.get_config()
        self.save_config(self.config)

    def load_config(self):
        try:
            text = Path(self.configpath).read_text()
            return yaml.safe_load(text)
        except IOError as exc:
            if exc.errno == errno.ENOENT:
                return None
            else:
                raise

    def get_config(self):
        config_yaml = self.load_config()
        if config_yaml is None:
            return DEFAULT_CONFIG

        overrides = config_yaml.get("override", {})
        config_yaml["override"] = {
            resolve_path(k): parse_override(v) for k, v in overrides.items()
        }

        return config_yaml

    def save_config(self, config):
        yaml.SafeDumper.add_representer(
            type(None),
            lambda dumper, value: dumper.represent_scalar("tag:yaml.org,2002:null", ""),
        )
        config["override"] = {
            unresolve(k, self.home): unparse_override(v)
            for k, v in config.get("override", {}).items()
        }

        text = jsondump(config)
        text = yaml.safe_dump(config, default_flow_style=False)

        Path(self.configpath).write_text(to_string(text))
        self.config = self.get_config()

    def venv_path(self, name):
        return os.path.join(self.venvspath, self.current_pythonbuild_name or "", name)

    @property
    def current_venv_path(self):
        """Returns the path of the currently active
        virtual environment.
        """
        return os.environ.get("VIRTUAL_ENV") or ""

    @property
    def current_venv_python_path(self):
        """If a virtual environment is activated, return the
        path to the python executable. Otherwise, return None.
        """
        if self.current_venv_path:
            return os.path.join(self.current_venv_path, "bin/python")

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

        config = self.get_config()
        return get_likely_projfolder(self.cwd, self.home, config=config)

    @property
    def correct_venv_name(self):
        """Returns the name of the virtualenvironment that
        should be active for this project. If we're not within
        a project, return an empty string.
        """

        for k, v in self.config["override"].items():
            if self.cwd.startswith(k):
                venvname = v["venvname"]
                if venvname:
                    return venvname

        likely = self.likely_projfolder
        return os.path.split(likely or "")[1]

    @property
    def correct_venv_path(self):
        return self.venv_path(self.correct_venv_name)

    def venv_exists(self, name):
        return os.path.exists(self.venv_path(name))

    def activate_path(self, name):
        return os.path.join(self.venv_path(name), "bin/activate")

    def pip_path(self, name):
        return os.path.join(self.venv_path(name), "bin/pip")

    def make_virtualenv(self, name):
        """Make a new virtual environment with the given name.

        """
        new_path = self.venv_path(name)

        tokens = shlex.split(self.virtualenv_creation_prefix)
        tokens.append(new_path)

        if not os.path.isdir(new_path):
            subprocess.call(tokens)
        else:
            print("PROBLEM: A virtualenv already exists at", new_path)

    def delete_virtualenv(self, name):
        path = self.venv_path(name)
        print("DELETING VIRTUALENV:", path)
        shutil.rmtree(path)

    @property
    def venv_active(self):
        return not not self.current_venv_path

    @property
    def correct_venv_active(self):
        return self.current_venv_path == self.correct_venv_path

    @property
    def pythonbuilds_current(self):
        return os.path.join(self.pyversionspath, "current")

    @property
    def pythonversion_path(self):
        if self.current_pythonbuild_name:
            return os.path.join(self.pyversionspath, self.current_pythonbuild_name)

    @property
    def shortversion(self):
        version = self.current_pythonbuild_name
        version_tokens = version.split(".")
        short = ".".join(version_tokens[:2])
        return short

    @property
    def python_path(self):
        p = self.pythonversion_path

        if p:
            suffix = "bin/python"
            return os.path.join(p, suffix)
        else:
            return sys.executable

    @property
    def virtualenv_creation_prefix(self):
        p_python = self.python_path

        if os.path.exists(p_python):
            return "{} -m venv".format(shquote(p_python))

        raise ValueError("something went wrong finding a python")

    @property
    def pythonversion_file_path(self):
        projfolder = self.likely_projfolder
        if projfolder:
            return os.path.join(projfolder, ".python-version")
        else:
            return ""

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
                version_string = f.read().splitlines()[0].strip()
                if version_string:
                    return version_string

        for k, v in self.config["override"].items():
            if self.cwd_pathlib.name.startswith(k):
                pyversion = v["pyversion"]
                if pyversion:
                    return pyversion

        if os.path.exists(self.pythonbuilds_current):
            realpath = os.path.realpath(self.pythonbuilds_current)
            return os.path.split(realpath)[1]

    @property
    def should_use_framework_build(self):
        if os.path.exists(self.pythonversion_file_path):
            with io.open(self.pythonversion_file_path) as f:
                contents = f.read().strip().splitlines()
                if "use_framework_build" in contents:
                    return True

        return False

    @property
    def suggested_bash_command(self):
        return self.suggested_command(shell="bash")

    @property
    def suggested_fish_command(self):
        return self.suggested_command(shell="fish")

    def suggested_command(self, shell="bash"):
        """Generates the correct bash command to make sure that the
        appropriate virtualenv is activated for the project folder
        you're in (or to deactivate if you're not in a project folder).
        """
        wanted = self.correct_venv_name

        if wanted:
            command = ""

            if not os.path.exists(self.correct_venv_path):
                s = "echo 'AUTOVENV: creating virtual environment: {}{}'; "

                if self.current_pythonbuild_name:
                    version_info = " (using non-system python version {})".format(
                        self.current_pythonbuild_name
                    )
                else:
                    version_info = ""

                command += s.format(wanted, version_info)

                s = "{} {}; "
                command += s.format(
                    self.virtualenv_creation_prefix, shquote(self.correct_venv_path)
                )

            if not self.correct_venv_active:
                if shell == "fish":
                    extension = ".fish"
                else:
                    extension = ""

                path = "{0}{1}".format(
                    self.activate_path(self.correct_venv_name), extension
                )

                command += "source {0}".format(shquote(path))

            if command:
                if shell == "bash":
                    command = "eval " + command

            return command

        elif self.current_venv_name:
            command = "echo 'AUTOVENV: deactivating...' ; deactivate"

            command = "eval " + command
            return command
        return ""

    def recreate(self):
        if self.venv_active:
            self.delete_virtualenv(self.correct_venv_name)
            self.make_virtualenv(self.correct_venv_name)
        else:
            print(RECREATE_ERROR)

    @property
    def build_defs_path(self):
        return resource_filename(__name__, "python-build/share/python-build")

    def do_command(self, args):
        if args.bash:
            print(self.suggested_bash_command)
        elif args.fish:
            print(self.suggested_fish_command)
        elif args.recreate:
            self.recreate()
        elif args.info:
            if self.current_venv_path:
                print("Using this virtualenv: {}".format(self.current_venv_path))
            else:
                print("Using system environment")
            if self.current_venv_python_path:
                p = self.current_venv_python_path
                print("Using this python: {}".format(p))
                print("...which is really at: {}".format(os.path.realpath(p)))
            else:
                print("Using system python")

            print("Config and data stored in: {}".format(self.data_dir))

            fb = self.should_use_framework_build
            print("Using framework build?: {}".format(fb))

            pypath = self.pythonversion_path

            print("Looking for a python version at: {}".format(pypath))
            print("Exists?: {}".format(os.path.exists(pypath)))
            print("Current config:")
            print(self.config)

            print("Suggested command: {}".format(self.suggested_command()))

        elif args.builddefspath:
            print(self.build_defs_path)
        elif args.pyversionspath:
            print(self.pyversionspath)
        elif args.pyversionspath_framework:
            print(self.pyversionspath_framework)
        elif args.python_version:
            target = os.path.join(self.pyversionspath, args.python_version)
            rel_target = os.path.relpath(target, self.pyversionspath)
            link_name = self.pythonbuilds_current
            create_symlink(rel_target, link_name)
            print("Now using the python at: {}".format(target))

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys

import autovenv
from autovenv import get_likely_projfolder as pf

from pathlib import Path


def test_autovenv(tmpdir):
    tmpdir = Path(str(tmpdir))
    R_TXT = tmpdir / 'a/b/c/requirements.txt'
    OTHER = tmpdir / 'a/b/c/d/e/f2.py'

    DEEPEST = tmpdir / 'a/b/c/d/e'
    HOME = tmpdir / 'a/b'
    PROJFOLDER = tmpdir / 'a/b/c'
    PYTHONBUILDS = tmpdir / 'pythonbuilds'
    PYTHONBUILDS_VERSION = PYTHONBUILDS / '10.11.12'
    PYTHONBUILDS_VERSION_BIN = PYTHONBUILDS / '10.11.12/bin'
    PYTHONBUILDS_VERSION_BIN_PYTHON = PYTHONBUILDS / '10.11.12/bin/python'
    PYTHONBUILDS_VERSION_BIN_PYVENV = PYTHONBUILDS / '10.11.12/bin/pyvenv'
    PYTHONBUILDS_CURRENT = PYTHONBUILDS / 'current'

    # PYTHONBUILDS_CURRENT_BIN_PYTHON = PYTHONBUILDS / 'current/bin/python'
    # PYTHONBUILDS_CURRENT_BIN_PYVENV = PYTHONBUILDS / 'current/bin/pyvenv'

    PYTHONBUILDS_OTHERVERSION_BIN_PYTHON = PYTHONBUILDS / '10.11.13/bin/python'
    PYTHONBUILDS_OTHERVERSION_BIN_PYVENV = PYTHONBUILDS / '10.11.13/bin/pyvenv'

    VENVS_HOME = tmpdir / 'a/b/.virtualenvs'

    PYTHONVERSION_FILE_PATH = PROJFOLDER / '.python-version'

    OTHER.parent.mkdir(parents=True)
    PYTHONBUILDS_VERSION_BIN.mkdir(parents=True)

    for p in (R_TXT, OTHER):
        with p.open('wb'):
            pass

    assert pf(str(DEEPEST), str(tmpdir)) == str(PROJFOLDER)
    assert pf(str(DEEPEST), str(HOME)) == str(PROJFOLDER)
    assert pf(str(DEEPEST), str(DEEPEST)) == None  # flake8: noqa

    del os.environ['VIRTUAL_ENV']

    v = autovenv.VirtualEnvs(venv_home=str(VENVS_HOME),
                             home=str(HOME),
                             cwd=str(PROJFOLDER),
                             pythonbuilds=str(PYTHONBUILDS))

    assert v.correct_venv_name == 'c'
    assert v.current_venv_name == ''

    venv_loc = str(VENVS_HOME / v.correct_venv_name)

    EXPECTED = "eval echo 'AUTOVENV: creating virtual environment: c'; " + \
        "virtualenv -p {executable} {venv}; . {venv}/bin/activate; "

    assert v.suggested_bash_command == EXPECTED.format(
        venv=venv_loc,
        executable=sys.executable)

    # test with python-build functionality

    assert v.pythonbuilds_current == str(PYTHONBUILDS_CURRENT)
    assert v.virtualenv_creation_prefix == 'virtualenv -p {}'.format(
        sys.executable)

    assert v.current_pythonbuild_name is None
    os.symlink(str(PYTHONBUILDS_VERSION), str(PYTHONBUILDS_CURRENT))

    assert os.path.exists(str(PYTHONBUILDS_CURRENT))
    assert v.current_pythonbuild_name == '10.11.12'
    with PYTHONBUILDS_VERSION_BIN_PYTHON.open('w'):
        pass

    with PYTHONBUILDS_VERSION_BIN_PYVENV.open('w'):
        pass

    assert v.python_path == str(PYTHONBUILDS_VERSION_BIN_PYTHON)
    assert v.pyvenv_path == str(PYTHONBUILDS_VERSION_BIN_PYVENV)

    with PYTHONVERSION_FILE_PATH.open('w') as f:
        f.write('10.11.13')

    assert v.python_path == \
        str(PYTHONBUILDS_OTHERVERSION_BIN_PYTHON)
    assert v.pyvenv_path == \
        str(PYTHONBUILDS_OTHERVERSION_BIN_PYVENV)

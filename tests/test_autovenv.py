from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

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

    VENVS_HOME = tmpdir / 'a/b/.virtualenvs'

    OTHER.parent.mkdir(parents=True)

    for p in (R_TXT, OTHER):
        with p.open('wb'):
            pass

    assert pf(str(DEEPEST), str(tmpdir)) == str(PROJFOLDER)
    assert pf(str(DEEPEST), str(HOME)) == str(PROJFOLDER)
    assert pf(str(DEEPEST), str(DEEPEST)) == None

    del os.environ['VIRTUAL_ENV']

    v = autovenv.VirtualEnvs(venv_home=str(VENVS_HOME),
                             home=str(HOME),
                             cwd=str(PROJFOLDER))

    assert v.correct_venv_name == 'c'
    assert v.current_venv_name == ''

    venv_loc = str(VENVS_HOME / v.correct_venv_name)

    EXPECTED = "eval echo 'AUTOVENV: creating virtual environment: c'; " + \
        "virtualenv {venv}; {venv}/bin/pip install --upgrade pip; " + \
        ". {venv}/bin/activate; "

    assert v.suggested_bash_command == EXPECTED.format(venv=venv_loc)

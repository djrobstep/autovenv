import os
import sys

import autovenv
from autovenv import get_likely_projfolder as pf, file_exists, DEFAULT_CONFIG

from pathlib import Path


def test_autovenv(monkeypatch, tmpdir):
    tmpdir = Path(str(tmpdir))

    subdir = tmpdir / "subdir"

    assert not file_exists(str(subdir))
    autovenv.mkdir_p(str(subdir))
    assert file_exists(str(subdir))
    autovenv.mkdir_p(str(subdir))
    assert file_exists(str(subdir))

    symlink = tmpdir / "symlink"
    autovenv.create_symlink(str(subdir), str(symlink))
    assert symlink.resolve() == subdir

    R_TXT = tmpdir / "a/b/c/requirements.txt"
    OTHER = tmpdir / "a/b/c/d/e/f2.py"

    DEEPEST = tmpdir / "a/b/c/d/e"
    HOME = tmpdir / "a/b"
    DATA_DIR = HOME / "datadir"
    PROJFOLDER = tmpdir / "a/b/c"
    PYTHONBUILDS = DATA_DIR / "pythonbuilds"
    PYTHONBUILDS_VERSION = PYTHONBUILDS / "10.11.12"
    PYTHONBUILDS_VERSION_BIN = PYTHONBUILDS / "10.11.12/bin"
    # PYTHONBUILDS_VERSION_BIN_PYTHON = PYTHONBUILDS / "10.11.12/bin/python"
    # PYTHONBUILDS_VERSION_BIN_PYVENV = PYTHONBUILDS / "10.11.12/bin/pyvenv"
    PYTHONBUILDS_CURRENT = PYTHONBUILDS / "current"

    # PYTHONBUILDS_CURRENT_BIN_PYTHON = PYTHONBUILDS / "current/bin/python"
    # PYTHONBUILDS_CURRENT_BIN_PYVENV = PYTHONBUILDS / "current/bin/pyvenv"

    # PYTHONBUILDS_OTHERVERSION_BIN_PYTHON = PYTHONBUILDS / "10.11.13/bin/python"
    # PYTHONBUILDS_OTHERVERSION_BIN_PYVENV = PYTHONBUILDS / "10.11.13/bin/pyvenv"

    if sys.platform == "darwin":
        VENVS_HOME = HOME / ".autovenv"
    else:
        VENVS_HOME = DATA_DIR / "venvs"

    # PYTHONVERSION_FILE_PATH = PROJFOLDER / ".python-version"

    VIRTUAL_ENV = None

    def environget(name, default=None):
        if name == "VIRTUAL_ENV":
            return VIRTUAL_ENV
        else:
            try:
                return os.environ[name]
            except KeyError:
                return default

    monkeypatch.setattr(os.environ, "get", environget)

    OTHER.parent.mkdir(parents=True)
    PYTHONBUILDS_VERSION_BIN.mkdir(parents=True)

    for p in (R_TXT, OTHER):
        with p.open("w"):
            pass

    assert pf(str(DEEPEST), str(tmpdir), config=DEFAULT_CONFIG) == str(PROJFOLDER)
    assert pf(str(DEEPEST), str(HOME), config=DEFAULT_CONFIG) == str(PROJFOLDER)
    assert pf(str(DEEPEST), str(DEEPEST), config=DEFAULT_CONFIG) is None

    v = autovenv.VirtualEnvs(
        data_dir=str(DATA_DIR), home=str(HOME), cwd=str(PROJFOLDER)
    )

    assert v.config == DEFAULT_CONFIG

    CONFIG = {"file_names": ["requirements.txt", "setup.py"]}
    v.save_config(CONFIG)
    assert v.config == CONFIG

    assert v.correct_venv_name == "c"
    assert v.current_venv_name == ""

    venv_loc = str(VENVS_HOME / v.correct_venv_name)

    C1 = "eval echo 'AUTOVENV: creating virtual environment: c'; "
    C2 = "virtualenv -p {executable} {venv}; source {venv}/bin/activate"
    EXPECTED = C1 + C2

    assert v.suggested_bash_command == EXPECTED.format(
        venv=venv_loc, executable=sys.executable
    )

    # test with python-build functionality

    # assert v.pythonbuilds_current == str(PYTHONBUILDS_CURRENT)
    assert v.virtualenv_creation_prefix == "virtualenv -p {}".format(sys.executable)

    assert v.current_pythonbuild_name is None
    os.symlink(str(PYTHONBUILDS_VERSION), str(PYTHONBUILDS_CURRENT))

    assert os.path.exists(str(PYTHONBUILDS_CURRENT))

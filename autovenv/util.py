import os
import errno

import json
import sys
import six

PY2 = sys.version_info[0] < 3

if not PY2:
    unicode = str


def to_string(x):
    if isinstance(x, six.binary_type):
        return x.decode('utf-8')
    return x


def jsondump(x):
    j = json.dumps(
        x,
        sort_keys=True,
        indent=4,
        separators=(',', ': '))
    return to_string(j) + '\n'


def file_exists(fpath):
    return os.path.exists(fpath)


def resolve_path(p):
    return os.path.realpath(os.path.abspath(os.path.expanduser(p)))


def unresolve(path, homepath):
    if path.startswith(homepath):
        path = path.replace(homepath, '~', 1)
    return path


def create_symlink(
        target,
        link_name,
        fail_if_exists=False,
        temporary_suffix='_temporary_symlink'):
    """
    Creates a symlink. If a symlink of this link name already exists, replace it.
    """

    if fail_if_exists and file_exists(link_name):
        raise OSError(
            "won't create symlink cos file already exists: {}".format(link_name))

    tempname = link_name + temporary_suffix
    os.symlink(target, tempname)
    os.rename(tempname, link_name)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

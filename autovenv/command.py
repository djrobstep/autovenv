import sys
import argparse

from .virtualenvs import VirtualEnvs


def parse_args(args):
    parser = argparse.ArgumentParser(description="Work with venvs and python versions.")
    parser.set_defaults(
        info=False,
        bash=False,
        fish=False,
        python_version=False,
        recreate=False,
        builddefspath=False,
        pyversionspath=False,
        pyversionspath_framework=False,
    )
    subparsers = parser.add_subparsers()

    bash = subparsers.add_parser(
        "bash",
        help="suggests a bash command that"
        " (hopefully) will activate the correct venv for this project",
    )
    bash.set_defaults(bash=True)

    fish = subparsers.add_parser(
        "fish",
        help="suggests a fish command that"
        " (hopefully) will activate the correct venv for this project",
    )
    fish.set_defaults(fish=True)

    recreate = subparsers.add_parser(
        "recreate", help="wipe the current virtualenv" " and reinstall it from scratch"
    )
    recreate.set_defaults(recreate=True)

    info = subparsers.add_parser(
        "info", help="show the current virtual" " environment and python version in use"
    )
    info.set_defaults(info=True)

    builddefspath = subparsers.add_parser(
        "builddefspath",
        help="returns the path where" "the python-build definitions are stored",
    )
    builddefspath.set_defaults(builddefspath=True)

    pyversionspath = subparsers.add_parser(
        "pyversionspath", help="returns the path where built python versions are stored"
    )
    pyversionspath.set_defaults(pyversionspath=True)

    pyversionspath_framework = subparsers.add_parser(
        "pyversionspath_framework",
        help="returns the path where built python versions are stored, if they are framework builds",
    )
    pyversionspath_framework.set_defaults(pyversionspath_framework=True)

    choose = subparsers.add_parser("choose", help="set your preferred python version")
    choose.add_argument(
        "python_version",
        help="your preferred python version "
        '(see possible versions with "autovenv-pythons-available")',
    )

    if not args:
        parser.print_help()
        return
    else:
        args = parser.parse_args(args)

    return args


def run(args):
    v = VirtualEnvs()
    v.do_command(args)


def do_command():  # pragma: no cover
    """Entry point for the 'autovenv' command.

    Simply creates a VirtualEnvs object with default parameters,
    and runs the command via that.
    """
    args = parse_args(sys.argv[1:])
    status = run(args)
    sys.exit(status)

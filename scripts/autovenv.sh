#!/usr/bin/env bash

do_autovenv() {
    $(autovenv bash)
}

cd() {
    builtin cd "$@" && do_autovenv
}

do_autovenv

#!/usr/bin/env fish

function do_autovenv
    eval (autovenv fish)
end

function cd
    builtin cd $argv
    and do_autovenv
end

do_autovenv

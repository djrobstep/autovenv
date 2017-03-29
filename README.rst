autovenv: virtualenv with less hassle
=====================================

    *I don't want to be a product of my environment, I want my environment to be a product of me.*

    -- Frank Costello in **The Departed**

Virtual environments are great, but they can be a bit annoying to create, manage, and switch between. autovenv takes the annoyance away.


Documentation
-------------

Full documentation is at `https://autovenv.readthedocs.org <https://autovenv.readthedocs.org>`_.


How It Works
------------

Basically, as long as there's a requirements.txt file in your python project, autovenv will figure out that the folder you're in is a python project, create a virtualenv for that project automatically, and activate/deactivate that virtualenv when you cd in/out of the project folder.

Here's how it works:

Just cd to anywhere within a python project, and autovenv will create a virtual environment for you if you don't have one already:

.. code-block:: shell
   :emphasize-lines: 1,6

    alex@xyz:~$ cd pyprojects/skynet
    AUTOVENV: creating virtual environment: skynet
    New python executable in /home/alex/.local/share/autovenv/venvs/skynet/bin/python
    Installing setuptools, pip, wheel...done.
    Requirement already up-to-date: pip in ...
    (skynet)alex@xyz:~/pyprojects/skynet$

(as you can see, it also checks that the pip within the virtualenv is up to date)

cd to a different project, it'll switch virtual environments automatically. cd out of a project and it'll deactivate the virtual environment.

autovenv tries to keep things tidy by storing config file, built python versions, and virtual environments in one app directory.

The location of this directory is platform-dependent (only linux it's at ~/.local/share/autovenv).

Locations:

  - <appdir>/config - the config file
  - <appdir>/pyversions - built python versions
  - <appdir>/venvs - virtual environments


Installation
------------

Simply install with `pip <https://pip.pypa.io>`_ globally, ie *not* within a virtual environment::

    $ pip install autovenv

and then add the following line to the end of your .bashrc file::

    source `which autovenv.sh`

or if you're using fish:

    source `which autovenv.fish`

That's it.

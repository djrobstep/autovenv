autovenv: virtualenv with less hassle
=====================================

    *I don't want to be a product of my environment, I want my environment to be a product of me.*

    -- Frank Costello in **The Departed**

Virtual environments are great, but they can be a bit annoying to create, manage, and switch between. It gets even worse when multiple different python versions come into play. **autovenv** takes the annoyance away.

*(Author's note: I wrote this package for my own use. It hasn't been publicly released for long so very much qualifies as alpha software, but hopefully you find it as handy as I do! It would be cool if you'd try it out. Issues/pull requests/etc would be even cooler).*

Basically, as long as there's a requirements.txt file in your python project, autovenv will figure out that the folder you're in is a python project, create a virtualenv for that project automatically, and activate/deactivate that virtualenv when you cd in/out of the project folder.

If you want to use a different python from your system python, autovenv helps with that too, by allowing you to build any of the different python versions out there, and use them with your virtualenvs.

How it Works
------------

Just cd to anywhere within a python project, and autovenv will create a virtual environment for you if you don't have one already, and activate it:

.. code-block:: shell
   :emphasize-lines: 1,6

  alex@xyz:~$ cd pyprojects/skynet
  AUTOVENV: creating virtual environment: skynet
  New python executable in /home/alex/.virtualenvs/skynet/bin/python
  Installing setuptools, pip, wheel...done.
  Requirement already up-to-date: pip in ...
  (skynet)alex@xyz:~/pyprojects/skynet$

cd to a different project, it'll switch virtual environments automatically. cd out of a project and it'll deactivate the virtual environment.

autovenv tries to keep things tidy by storing the virtualenvs it creates under ~/.virtualenvs

Using different pythons (optional but recommended)
--------------------------------------------------

By default, autovenv will create a virtualenv using your system python. That might be OK, but your needs are probably greater. You probably want to use the latest Python 3. And you might want to use cool alternative Pythons like PyPy as well.

Luckily autovenv has you covered on this. When you install autovenv you get python-build installed as well, customized to build pythons into a ~/.python-versions folder.

This makes things pretty easy. Let's see:

.. code-block:: shell
   :emphasize-lines: 1,7

    alex@xyz:~$ autovenv-build 3.5.1
    Downloading Python-3.5.1.tgz...
    -> https://www.python.org/ftp/python/3.5.1/Python-3.5.1.tgz
    Installing Python-3.5.1...
    Installed Python-3.5.1 to /home/alex/.python-versions/3.5.1

    alex@xyz:~$ python --version
    Python 2.7.10

So we've built 3.5.1, but our system python is unchanged and still active.

.. code-block:: shell
   :emphasize-lines: 1

    alex@xyz:~$ autovenv choose 3.5.1
    Now using the python at: ~/.python-versions/3.5.1

This python will now be used when creating/activating virtual environments:

.. code-block:: shell
   :emphasize-lines: 1,4

    alex@xyz:~$ cd pyprojects/skynet
    (skynet)alex@xyz:~/pyprojects/skynet$ python --version
    Python 3.5.1
    (skynet)alex@xyz:~/pyprojects/skynet$ autovenv info
    Using this virtualenv: ~/.virtualenvs/3.5.1/autovenv
    using the python at: ~/.virtualenvs/3.5.1/autovenv/bin/python
    ...which is really at: ~/.python-versions/3.5.1/bin/python3.5

To list the available pythons you can install, use autovenv-pythons-available to see the versions available:

.. code-block:: shell
   :emphasize-lines: 1

    alex@xyz:~$ autovenv-pythons-available
    2.7.11
    ...
    3.5.1
    ...
    pypy3-dev
    ...


Installation
------------

Simply install with `pip <https://pip.pypa.io>`_ globally, ie *not* within a virtual environment:

.. code-block:: shell

    $ pip install autovenv

and then add the following line to the end of your .bashrc file:

.. code-block:: shell

    source `which autovenv.sh`

That's it!

When building python versions, you may need to install some development packages on your system. For Ubuntu, this command may help:

.. code-block:: shell

    $ sudo apt-get install build-essential zlib1g-dev libbz2-dev libssl-dev libreadline-dev libncurses5-dev libsqlite3-dev libgdbm-dev libdb-dev libexpat-dev libpcap-dev liblzma-dev libpcre3-dev


Useful Links
------------

Source Code: `github.com/djrobstep/autovenv <https://github.com/djrobstep/autovenv>`_

PyPI package info: `autovenv@PyPI <https://pypi.python.org/pypi/autovenv>`_


Internals
---------

.. toctree::
   :maxdepth: 2

   api.rst

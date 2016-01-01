autovenv: virtualenv with less hassle
=====================================

    *I don't want to be a product of my environment, I want my environment to be a product of me.*

    -- Frank Costello in **The Departed**

Virtual environments are great, but they can be a bit annoying to create, manage, and switch between. autovenv takes the annoyance away.

*(Author's note: I created autovenv for my own use and am now chucking the code up on github and pypi very much as alpha software. It would be cool if you'd try it out. Issues/pull requests/etc would be even cooler).*

Basically, as long as there's a requirements.txt file in your python project, autovenv will figure out that the folder you're in is a python project, create a virtualenv for that project automatically, and activate/deactivate that virtualenv when you cd in/out of the project folder.

Here's how it works:

Just cd to anywhere within a python project, and autovenv will create a virtual environment for you if you don't have one already, and activate it:

.. code-block:: shell
   :emphasize-lines: 1,6

    alex@xyz:~$ cd pyprojects/skynet
    AUTOVENV: creating virtual environment: skynet
    New python executable in /home/alex/.virtualenvs/skynet/bin/python
    Installing setuptools, pip, wheel...done.
    Requirement already up-to-date: pip in ...
    (skynet)alex@xyz:~/pyprojects/skynet$

(as you can see, it also checks that the pip within the virtualenv is up to date)

cd to a different project, it'll switch virtual environments automatically. cd out of a project and it'll deactivate the virtual environment.

autovenv tries to keep things tidy by storing the virtualenvs it creates under ~/.virtualenvs

Installation
------------

Simply install with `pip <https://pip.pypa.io>`_::

    $ pip install autovenv

and then add the following line to the end of your .bashrc file::

    source `which autovenv.sh`

That's it.


Useful Links
------------

Source Code: `github.com/djrobstep/autovenv <https://github.com/djrobstep/autovenv>`_

PyPI package info: `autovenv@PyPI <https://pypi.python.org/pypi/autovenv>`_


Internals
---------

.. toctree::
   :maxdepth: 2

   api.rst
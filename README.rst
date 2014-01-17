=====
Henry
=====

Henry is a GitHub issues cli

Features
--------

* lists issues
* saves issues locally so you can look at them even while on the road


:Code:         https://github.com/willkg/henry/
:Issues:       https://github.com/willkg/henry/issues
:License:      BSD 3-clause; See LICENSE
:Contributors: See AUTHORS.rst


Status
======

I wrote this on a lark to meet a personal need. If you're interested
in continuing this work, let me know. Otherwise, it's just going to
hang out as it is for the foreseeable future.


Install
=======

From PyPI
---------

Run::

    $ pip install henry


For hacking
-----------

Run::

    $ git clone https://github.com/willkg/henry
    # Create a virtualenvironment
    $ pip install -e .


Usage
=====

List all the issues for a repository:

::

    $ henry-cmd list


View the details of a specific issue:

::

    $ henry-cmd view [num]


Cache the issue list and details locally so you can view things while
on a plane:

::

    $ henry-cmd cache


Using non-origin remotes
------------------------

All three commands default to using the `origin` remote. If that's not
the remote that has the issues, pass in the ``--remote [REMOTENAME]``
argument.

Example::

    $ henry-cmd view --remote upstream


Authenticated and unauthenticated GitHub API access
---------------------------------------------------

All three commands will default to using the unauthenticated GitHub
API access. You get ratelimited to 60 requests per hour.

To use the authenticated GitHub API access, you need to create a
GitHub account token. See the instructions here:

https://help.github.com/articles/creating-an-access-token-for-command-line-use

After creating a token, put your username and token separated by a
colon in a file called ``~/.githubauth``. For example::

    willkg:aifjaslkdf484jlkakhskfdhad

If that file exists, Henry will automatically use it.


Using Henry when you're not connected to the Internet
-----------------------------------------------------

When you use the ``view`` and ``list`` commands and you're not
connected to the Internet, Henry will automatically pull from
cache. Yay!


What to do before you get on a plane
------------------------------------

Go through the repositories you're interested in viewing issues from
and run::

    $ henry-cmd cache

That'll cache issue data locally.

========================
Previz Python API Client
========================

The Previz Python API client provides a clean interface for accessing version 2 of `the Previz REST API <https://previz.co>`_.

Both this client and the v2 API are a work-in-progress. At present, the client is primarily focussed on provided the functionality required by the integration plugins.

As the v2 API matures, the Python client will be updated to provide more general purpose functionality.

-----------------
Supported actions
-----------------

The current version of the Previz Python API client supports the following actions:

- Retrieve all assets for a given project
- Retrieve a single asset, identified by its UUID
- Retrieve all plugins
- Retrieve all projects
- Retrieve a single project, identified by its UUID
- Retrieve all scenes
- Retrieve a single scene, identified by its UUID
- Retrieve all teams
- Retrieve a single team, identified by its UUID

Some actions may be restricted to users with specific permissions.

-----------
Development
-----------

^^^^^^^^^^^^^^^
Getting started
^^^^^^^^^^^^^^^

The following instructions are specific to macOS, and make the following assumptions:

1. The command line doesn't fill you with fear. If it does, you're very lost right now.
2. You have installed `Homebrew <https://homebrew.sh>`_ on your machine.
3. You're setting everything up from scratch. If you've already installed a bunch of Python-related stuff on your machine, chances are you're going to run into problems.
4. You don't have any strong feelings regarding Python dependency management and test runners, other than a general desire not to waste your life wading through those particular quagmires.

If you already have your own preferred way of doing things, that's fine; just be aware that Your Setup™ is not supported.

If you're not running macOS, then you have some work ahead of you. Sorry about that, we all use macOS, and this is primarily an internal tool at present.

.. code-block:: bash

   # Install tox globally, using your system Python
   pip install tox

   # Install pyenv, for easy management of multiple Python versions
   brew install pyenv

   # Install the Python versions we want to test against
   pyenv install 2.7.14
   pyenv install 3.5.5
   pyenv install 3.6.4

   # Set the "global" pyenv versions
   pyenv global 2.7.14 3.5.5 3.6.4

   # Sanity check...
   pyenv global
   2.7.14
   3.5.5
   3.6.4

You'll probably also want to add the following code to your ``.(bash|z|whatever)rc`` file, to ensure that `pyenv` is initialised correctly whenever the shell is loaded.

.. code-block:: bash

   if [ -x "$(command -v pyenv)" ]; then
       eval "$(pyenv init -)"
   fi

^^^^^^^^^^^^^^^^^
Running the tests
^^^^^^^^^^^^^^^^^

.. code-block:: bash

   cd /path/to/previz-python-api
   tox

Tox will automatically create the required virtual environments for Python 2.7, 3.5, and 3.6, using the "global" pyenv-managed Python versions, and run the tests.

Note that you *do not* need to create your own virtual environments. In fact, you *must not* run ``tox`` from within a ``venv`` or ``virtualenv`` environment.

Also, it's worth mentioning that running the tests using ``detox`` is not currently supported. For reasons unclear, certain test environments throw an error, and the test suite currrently isn't large enough to warrant spending any time implementing parallel execution of tests.

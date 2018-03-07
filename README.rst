##########
Museum Map
##########

Run the instruction for the initial fetch first. Then all further command
sets should be run inside the checked out directory.

Dependencies
============

The following core Debian packages are required:

* Software Packages
  * PostgreSQL server: postgresql
  * Python 3: python3
  * Python 3 dev: python3-dev
  * Libxslt dev: libxslt1-dev
  * Pip: python3-pip
  * Supervisor: supervisor
* Python Packages
  * Pipenv: sudo pip3 install pipenv

The database user and password need to be set up once:

.. sourcecode:: console

  $ sudo -u postgres /usr/bin/createuser -P DBUSER
  $ sudo -u postgres /usr/bin/createdb --owner=DBUSER DBNAME

The first command will ask for a password to be used when configuring the application.

Initial Fetch
=============

.. sourcecode:: console

  $ hg clone ssh://hg@bitbucket.org/mhall/museum-map

(Re)build
=========

Updates the software and (re-)runs the full installation and data processing
steps:

.. sourcecode:: console

  $ hg pull --update
  $ export PIPENV_VENV_IN_PROJECT=True
  $ pipenv install --three
  $ pipenv run pip install .
  $ pipenv run pip install psycopg2
  $ pipenv run python -m spacy download en
  $ pipenv run MuseumMap generate_config production.ini postgresql+psycopg2://DBUSER:DBPASS@localhost/DBNAME
  $ pipenv run MuseumMap init_database production.ini --drop-existing
  $ pipenv run MuseumMap load_data production.ini PATH_TO_DATA_FILE
  $ pipenv run MuseumMap generate_hierarchy production.ini
  $ pipenv run MuseumMap link_wikipedia production.ini

By default the server runs only on localhost. To run it on an external IP, replace the ``MuseumMap generate_config``
line with the following:

.. sourcecode:: console

  $ pipenv run MuseumMap generate_config production.ini postgresql+psycopg2://DBUSER:DBPASS@localhost/DBNAME --host IP

Update
======

Updates the software and dependencies, but does not touch the data

.. sourcecode:: console

  $ hg pull --update
  $ export PIPENV_VENV_IN_PROJECT=True
  $ pipenv install
  $ pipenv run pip install .

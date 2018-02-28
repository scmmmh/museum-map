##########
Museum Map
##########

Run the instruction for the initial fetch first. Then all further command
sets should be run inside the checked out directory.

Initial Fetch
=============

.. sourcecode:: console

  $ hg clone ssh://hg@bitbucket.org/mhall/museum-map

(Re)build
=========

Updates the software and (re-)runs the full installation and data processing
steps.

.. sourcecode:: console

  $ hg pull --update
  $ pipenv install --three
  $ pipenv run pip install .
  $ pipenv run pip install psycopg2
  $ pipenv run python -m spacy download en
  $ pipenv run MuseumMap generate_config production.ini SQLALCHEMY_CONNECTION_STRING
  $ pipenv run MuseumMap init_database production.ini --drop-existing
  $ pipenv run MuseumMap load_data production.ini PATH_TO_DATA_FILE
  $ pipenv run MuseumMap link_wikipedia production.ini
  $ $ pipenv run MuseumMap generate_hierarchy production.ini

Update
======

Updates the software and dependencies, but does not touch the data

.. sourcecode:: console

  $ hg pull --update
  $ pipenv install
  $ pipenv run pip install .

#!/bin/bash
hg pull --update
export PIPENV_VENV_IN_PROJECT=True
pipenv install
pipenv run pip install .

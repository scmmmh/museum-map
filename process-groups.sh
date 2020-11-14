#!/bin/bash

python -m museum_map -c development.ini groups generate-groups
python -m museum_map -c development.ini groups merge-singular-plural
python -m museum_map -c development.ini groups add-parent-groups
python -m museum_map -c development.ini groups prune-single-groups
python -m museum_map -c development.ini groups move-inner-items

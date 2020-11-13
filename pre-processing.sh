#!/bin/bash

python -m museum_map -c development.ini processing generate-groups
python -m museum_map -c development.ini processing merge-singular-plural
python -m museum_map -c development.ini processing add-parent-groups
python -m museum_map -c development.ini processing prune-single-groups
python -m museum_map -c development.ini processing move-inner-items

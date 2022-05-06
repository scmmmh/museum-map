#!/bin/bash

# Run the web application
python -m museum_map -c /etc/museum-map/production.ini server run --port 8080

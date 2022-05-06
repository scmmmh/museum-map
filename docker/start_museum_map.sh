#!/bin/bash

DEFAULT_GATEWAY=`ip route show | grep "default via" | grep -E -o "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]"`

# Run the web application
python -m museum_map -c /etc/museum-map/production.ini server run --port 80

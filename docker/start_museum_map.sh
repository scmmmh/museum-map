#!/bin/bash

DEFAULT_GATEWAY=`ip route show | grep "default via" | grep -E -o "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]"`

sed -i -e "s#uri =.*#uri = $SQLALCHEMY_URL#g" \
       /etc/museum-map/production.ini

# Run the web application
python -m museum_map -c /etc/museum-map/production.ini -v server run --port 8080

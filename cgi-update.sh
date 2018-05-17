#!/bin/bash
echo "Content-Type: text/text"
echo ""
echo "Update started"
./update.sh 1>./build.log 2>./build-error.log &

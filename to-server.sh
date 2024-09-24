#!/bin/sh

set -e

scp -r $(realpath .) bbox-local:/root/srv/
ssh -t bbox-local -c "cd /root/srv/bardak; docker-compose down; docker-compose up --build"


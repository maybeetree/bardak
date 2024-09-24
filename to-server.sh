#!/bin/sh

set -e

rsync -avz $(git ls-files) bbox-local:/root/srv/bardak
ssh -t bbox-local "cd /root/srv/bardak; docker-compose down -t 1; docker-compose up --build -d"


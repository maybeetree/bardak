#!/bin/sh

set -e

rsync -avz $(git ls-files) bbox.home:/root/srv/bardak
ssh -t bbox.home "cd /root/srv/bardak; docker-compose down -t 1; docker-compose up --build -d"


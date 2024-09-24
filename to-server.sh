#!/bin/sh

set -e

rm -f things/*
rm -f trash/*
scp -r $(realpath .) bbox-local:/root/srv/
ssh -t bbox-local "cd /root/srv/bardak; docker-compose down; docker-compose up -d"


#!/bin/bash

docker compose -f ./app/docker-compose.yaml down
git pull
docker compose -f ./app/docker-compose.yaml up --build -d -y
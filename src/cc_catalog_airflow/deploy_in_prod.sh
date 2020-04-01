#!/bin/bash

read -r -p "Have you set up .env? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    docker-compose -f docker-compose.yml build webserver
    docker-compose -f docker-compose.yml up -d webserver
else
    echo "Please set up the environment first."
fi

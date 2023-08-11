#!/usr/bin/env bash


############################
# Installation
############################

# Distribution software
apt-get update
apt-get install -y docker.io vim tmux python3-dev python3-pip python-is-python3 curl postgresql-client

# Python packages
pip3 install pip invoke docker-compose==1.26 ipython


############################
# Start services
############################

# Cronjobs
update-rc.d cron defaults

# Docker
docker swarm init
gcloud auth configure-docker -q


############################
# Setup project
############################

cd /srv
gsutil rsync -r -J gs://ds-deploy/ .
mkdir -p data
cp server/datascope-cron /etc/cron.d/

gcloud secrets versions access 4 --secret=datascope-certificate-key > server/nginx/certificates/data-scope.key
gcloud secrets versions access 3 --secret=debatkijker-certificate-key > server/nginx/certificates/debatkijker.key


############################
# Start project
############################

# For Kibana to be able to connect to Elasticsearch it needs to get a service token
# Create a service token through the following page:
# https://www.elastic.co/guide/en/elasticsearch/reference/current/service-tokens-command.html
# Add the token as ELASTICSEARCH_SERVICE_TOKEN in the .env file.
# Copy the contents of the service_tokens file into the secrets directory of the environment.

invoke pull -v 0.20.3
invoke init production worker
invoke deploy

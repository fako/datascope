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
# Start project
############################

cd /srv
gsutil rsync -r -J gs://ds-deploy/ .
cp server/datascope-cron /etc/cron.d/
mkdir -p data
invoke pull
invoke init production web
invoke deploy


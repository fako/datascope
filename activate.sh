#!/usr/bin/env bash

source venv/bin/activate
export DJANGO_CONTEXT=host
export $(cat .env | xargs)

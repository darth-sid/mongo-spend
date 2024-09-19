#!/bin/sh
export FLASK_APP=./spend-api/index.py
flask --app ./spend-api/endpoints --debug run -h 0.0.0.0 -p 8000 --cert=adhoc


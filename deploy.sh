#!/bin/bash

set -e -x

if [ -n "$GIT_DATA_REPO" ]; then
    git clone --depth=1 "$GIT_DATA_REPO" data || true
    ( cd data && git pull --ff-only )
fi

pip3 install pipenv
pipenv sync
pipenv run ./generate.py
cp -r -T overlay .build/static
find

#!/usr/bin/env bash

echo Building pythonflasklogin
$(which docker) build -t pythonflasklogin:build -f Dockerfile.build .
$(which docker) build -t pythonflasklogin:latest --no-cache --build-arg "BASE_IMG=pythonflasklogin:build" .

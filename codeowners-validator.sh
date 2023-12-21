#!/bin/sh
docker run --rm -v "$(pwd):/repo" -e REPOSITORY_PATH=/repo -e OWNERCHECKER_REPOSITORY=/repo gmottajr/codeowners-validator:latest

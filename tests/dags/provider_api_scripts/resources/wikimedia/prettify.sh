#!/bin/bash

T=$(mktemp)
jq '.' $1 > $T
mv $T $1

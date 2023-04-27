#!/bin/bash
for b in $${BUCKETS_TO_CREATE//,/ }; do
    echo "Making bucket $$b" && mkdir -p /data/$$b;
    done &&
    exec $$0 "$$@"
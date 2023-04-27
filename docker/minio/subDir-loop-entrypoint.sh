#!/bin/bash
/usr/bin/mc config host add s3 http://s3:5000 ${AWS_ACCESS_KEY} ${AWS_SECRET_KEY};
cd /data;
    for b in */ ; do
       echo "Loading bucket $b"
       /usr/bin/mc mb --ignore-existing s3/$b
       /usr/bin/mc cp --r $b s3/$b
       /usr/bin/mc ls s3/$b;
    done ;
    exit 0;

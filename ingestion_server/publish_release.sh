# Usage: ./public_release.sh [VERSION]
docker build -t creativecommons/ingestion_server:$1 . &
docker build -f Dockerfile-worker -t creativecommons/indexer_worker:$1 .
docker push creativecommons/ingestion_server:$1 &
docker push creativecommons/indexer_worker:$1

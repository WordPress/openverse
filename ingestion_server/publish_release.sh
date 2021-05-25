# Usage: ./public_release.sh [VERSION]
docker build -t openverse/ingestion_server:$1 .
docker build -f Dockerfile-worker -t openverse/indexer_worker:$1 .
docker push openverse/ingestion_server:$1
docker push openverse/indexer_worker:$1

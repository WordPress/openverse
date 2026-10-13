# Troubleshooting

This guide describes various manual steps to troubleshoot issues with the
ingestion server's processes like database transfer, ES indexing.

## Interrupt indexing

The ingestion server performs indexing using indexer workers, whose primary
purpose it is to create documents from the API database and index them in
Elasticsearch.

Indexer workers are EC2 instances that are stopped by default when indexing is
not taking place. The ingestion server raises them up, provides them with the
necessary information to perform the indexing and once they report back to the
ingestion server with a completion message, they are shut down again.

Sometimes it is necessary to manually interrupt indexing, for example to limit
the size of a test/staging index. To do so, follow these steps.

1. Determine the active ingestion worker machines from the AWS EC2 dashboard.
   They will be named `indexer-worker-(dev|prod)` and will be in the "running"
   state.

2. SSH into the machine using it's public IP.

   ```console
   $ ssh ec2-user@<public-ip>
   ```

3. Determine the name of the active `indexer_worker` container and pause it.

   ```console
   $ docker ps
   $ docker pause <container_id>
   ```

4. Repeat steps 2 and 3 for each active ingestion worker machine. Leave the SSH
   sessions open.

5. Wait for a few minutes and note the document count in the Elasticsearch index
   that was currently being created. It may increase a little because of timing
   effects but should stop after a few minutes.

6. From each of the open SSH sessions, send a completion notification to the
   ingestion server's internal IP address.

   ```console
   $ curl \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"error":false}' \
     http://<internal-ip>:8001/worker_finished
   ```

7. Terminate the SSH sessions and stop the indexer worker EC2 machines from the
   AWS EC2 dashboard.

8. The ingestion server will the instruct ES to start the next step of indexing,
   i.e. replication.

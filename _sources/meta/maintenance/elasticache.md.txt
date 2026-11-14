# ElastiCache maintenance

This document covers applying service updates to the API's Redis caches,
`api-cache-dev` in staging and `api-cache-prod` in production.

AWS doesn't apply most ElastiCache service updates automatically, so security
fixes can stay unapplied until someone applies them. Check for updates when a
Redis CVE is announced, and regularly otherwise. To see whether an update fixes
a CVE, check the
[ElastiCache CVE table](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/cve.html).

## Checking for updates

List the updates for a cache. Replace `<cache>` with the name of the cache.

```bash
aws elasticache describe-update-actions --region us-east-1 \
  --cache-cluster-ids <cache> \
  --update-action-status not-applied waiting-to-start in-progress stopping stopped scheduling scheduled complete not-applicable \
  --query 'UpdateActions[].[ServiceUpdateName,ServiceUpdateStatus,UpdateActionStatus,NodesUpdated]' \
  --output table
```

- Only updates with a service update status of `available` or `scheduled` can be
  applied. Expired updates can't be applied, and need no action.
- Updates are cumulative, so applying the newest update also covers older ones.
- The action status of older updates can take a while to change to `complete`.

## Applying an update

Applying an update interrupts the cache, and the API can't reach it for a short
time. Apply each update to staging first. These steps don't change Terraform,
because the engine version in Terraform doesn't change.

1. Take a manual snapshot, then wait for its status to be `available`.

   ```bash
   aws elasticache create-snapshot --region us-east-1 \
     --cache-cluster-id <cache> --snapshot-name <cache>-pre-patch-<yyyymmdd>
   aws elasticache describe-snapshots --region us-east-1 \
     --snapshot-name <cache>-pre-patch-<yyyymmdd> \
     --query 'Snapshots[0].SnapshotStatus' --output text
   ```

2. Apply the update.

   ```bash
   aws elasticache batch-apply-update-action --region us-east-1 \
     --service-update-name <service_update_name> --cache-cluster-ids <cache>
   ```

3. Rerun the command from [Checking for updates](#checking-for-updates) until
   the update is `complete`.

4. Check that the cache kept its items. A sudden drop to near zero means the
   cache lost its data. These `date` flags are for macOS.

   ```bash
   aws cloudwatch get-metric-statistics --region us-east-1 \
     --namespace AWS/ElastiCache --metric-name CurrItems \
     --dimensions Name=CacheClusterId,Value=<cache> Name=CacheNodeId,Value=0001 \
     --start-time "$(date -u -v-3H +%Y-%m-%dT%H:%M:%SZ)" \
     --end-time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
     --period 300 --statistics Average \
     --query 'sort_by(Datapoints,&Timestamp)[].[Timestamp,Average]' --output table
   ```

5. Check that Terraform shows no changes. Run this from the infrastructure
   repository, using `next/staging staging-api` or
   `next/production production-api`.

   ```bash
   just plan next/staging staging-api
   ```

6. Once production is patched and healthy, delete the snapshots. Manual
   snapshots don't expire, and you can't undo this.

   ```bash
   aws elasticache delete-snapshot --region us-east-1 \
     --snapshot-name <cache>-pre-patch-<yyyymmdd>
   ```

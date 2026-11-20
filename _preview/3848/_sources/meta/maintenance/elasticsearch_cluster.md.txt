# Elasticsearch cluster maintenance

This document covers upgrading and making configuration changes to our
Elasticsearch clusters. The audience of this document is Openverse maintainers
with access to Openverse's infrastructure.

## External resources

### Documentation

```{warning}
The following links are pinned to the "current" version. You can switch between
specific Elasticsearch versions via the version dropdown at the top of the
table of contents on the right side of the webpage.
```

- [Migration guides](https://www.elastic.co/guide/en/elasticsearch/reference/current/breaking-changes.html)
- [Rest API](https://www.elastic.co/guide/en/elasticsearch/reference/current/rest-apis.html)
- [Cluster configuration](https://www.elastic.co/guide/en/elasticsearch/reference/current/settings.html)

### Dependencies

- [`elasticsearch-py`](https://github.com/elastic/elasticsearch-py)
- [`elasticsearch-dsl`](https://github.com/elastic/elasticsearch-dsl-py/)

## Version upgrades

Updating the Elasticsearch (ES) cluster involves three basic steps:

- Upgrade the Elasticsearch version used in local development
- Deploy staging and production clusters with the new version
- Upgrade the Elasticsearch client versions to match the new version
  - The API, ingestion server, and catalog all communicate with Elasticsearch
    and need attention during this step

The order of these steps, in particular when the client versions should be
updated, depends on the breaking changes in Elasticsearch, its clients, and
whether the clients are backwards or forwards compatible. The order above
represents a _forwards_ compatible client, one that works with the current and
new version of ES at the same time. Depending on the changes to the ES API and
the client, it may be necessary to upgrade the client first, in which case the
client would be _backwards_ compatible with the previous version.

For example, the ES 7 client was _forwards_ compatible with ES 8 through an
environment variable that enabled a compatibility mode. This meant we could
update the local ES instance and the live clusters to ES 8 before updating the
local clients without introducing a compatibility issue.

This guide primarily covers the process of upgrading the Elasticsearch cluster,
because it is both the most complicated and most stable process. While there are
several improvements that can be made to the current Elasticsearch Terraform
module that would ease this process, the current process works. The current pace
of ES updates is such that the existing process is sufficient for our purposes.

### Steps

#### 0. Read the Elasticsearch release notes

Before doing anything, read the release notes for each minor or major version we
are upgrading through. Pay special attention, of course, to major version
release notes and sections on breaking changes. Openverse's Elasticsearch usage
is relatively simple, and we often avoid issues with breaking changes on the
cluster side, but it is paramount to understand these breaking changes before
embarking on a cluster upgrade. In particular, note any configuration changes
that we need to make to the cluster via environment variables or if changes need
to be made to the deployment process. For example, pay attention to any changes
related to node registration, inter-cluster communication, and transport layer
security (i.e., HTTPS, client keys, or other such changes).

#### 1. Determine when to update the client version

The API and ingestion server use
[`elasticsearch-py` and `elasticsearch-dsl`](#dependencies) to build queries and
communicate with Elasticsearch. Both libraries support pinning client versions
to Elasticsearch version by
[appending the major version number to the end of the package name](https://github.com/elastic/elasticsearch-py#compatibility),
e.g., `elasticsearch7` for the ES 7 client version and `elasticsearch-dsl7` for
the DSL version for ES 7. This can be useful if Pipenv presents difficulties
with pinning a particular version.

Read the release notes for all ES client versions after the current client
version. **Check `Pipfile.lock` to confirm the current version as it may not
necessarily be the version in the `Pipfile`, particularly if it is only minor
version constrained (uses `~=X.X`)**. Patch versions shouldn't include breaking
changes, and neither should minor versions, but it's better to read the release
notes anyway than to find out later that there was an issue we needed to be
aware of ahead of time. If this is a major version upgrade, you should spend
extra time reading through the first major version release notes.
[Elastic publishes comprehensive and straightforward client migration documentation for major version releases](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/migration.html):
these notes are required reading for upgrading between major versions.

If the current client version is forwards compatible with the new ES version,
then the ES client should be upgraded last. For major version releases, it is
often only the _last_ minor version release of the client library that has a
forwards compatibility option, so it might be necessary to upgrade the clients
to the last minor version of the library. In this case, the cluster will be at
an earlier _minor_ version than the client expects. The ES client should be
okay, but it is designed to match the cluster version. Luckily our unit and
integration tests in the API and ingestion server are comprehensive enough to
have confidence in Elasticsearch client upgrade compatibility because our tests
run against a real Elasticsearch node, rather than through mocks. Still, better
safe than sorry, so read the release notes!

If the current client version is _not_ forwards compatible (perhaps because of a
security patch or change in cluster authentication) but is backwards compatible,
you must upgrade the client version before upgrading the cluster.

#### 2. Upgrade the client version if necessary

If in the previous step we determine that the current client version is not
forwards compatible, whether because it needs to be updated to a more recent
forwards compatible minor version or to a backwards compatible major version,
upgrade the client version now and deploy through to production. Confirm
services are stable.

#### 3. Upgrade the local Elasticsearch version

Update the local Elasticsearch version in the root `docker-compose.yml`. In step
0 we should have noted any configuration changes that will be necessary. The
Elasticsearch setup used locally is a single node setup, meaning it's generally
significantly simpler than the live clusters. **Do not take the ease with which
the local version is updated as an indication that the live cluster
configuration changes will be easy!** Elasticsearch configuration becomes
significantly more complicated when there are multiple nodes.

Make changes to
[`docker/es/env.docker`](https://github.com//WordPress/openverse/blob/9afc32ab703c692980ba7326d5b771e6bb754c97/docker/es/env.docker),
to update the configuration as necessary.

At this point CI and all integration tests should pass. If they do not, check
whether the issue is with the ES node configuration or with the client. Read
through release notes again to see if there's anything relevant and check the
GitHub repositories. Make changes as necessary. This is the first time when
integration between the application and the new ES version is being tested, so
it's critical that it passes. If changes to index settings or mappings are
necessary, these must be done in a way that is backwards compatible. The cluster
info API returns `cluster_name`, which can be used during runtime to swap
between mappings or index settings at runtime if necessary.

Add new CI steps to test the previous Elasticsearch version as well as the new
version. Do this by using an environment variable to configure the Elasticsearch
version used,
[as we did in this PR for the ES 7 to 8 upgrade](https://github.com/WordPress/openverse/pull/2832).
If new configuration changes do not work with the previous version, it will be
necessary to have distinct `docker/es/env.docker` files for each version,
configured via the same environment variable that determines the ES version.

Once everything passes for the current and new Elasticsearch versions and
changes are merged and deployed, this step is complete.

#### 4. Create the new Terraform module

Copy the current Elasticsearch Terraform module into a fully new module named
with the version in the directory name. For example, if upgrading to version
8.9.0, duplicate the existing Terraform module and name the new directory
`elasticsearch-8.9.0`[^past-foibles]. Make changes to the configuration based on
the release note reading done in previous steps (especially step 0), and deploy
the new cluster. It may take several attempts to successfully deploy the new
cluster. The critical things to ensure are:

1. All nodes successfully register with the cluster, including the expected
   number of data and master nodes based on the configuration.
1. All nodes have the correct resources allocated to the Elasticsearch process.
1. All configuration changes are reflected in the new cluster.

[Elasticvue is especially useful for this](https://elasticvue.com/), in
particular the "Nodes" tab, which gives a good overview of the cluster's nodes.
It also makes it easy to send REST API calls to the cluster for confirming
configurations if needed.

Tearing down and redeploying the new cluster over and over for each
configuration change during the initial deployment attempts can be cumbersome
and slow. Sometimes it will be easier to follow the
[instructions for in place configuration changes](#in-place-changes-to-live-nodes)
on the nodes in the new cluster until we have determined the correct final
configuration. The final successful deployment _must_ be from scratch: i.e., do
not treat an in-place configuration change as a success until the configuration
is verified to work for a wholly new cluster. Clusters must be able to spin up
in a fully configured state without further intervention for the module to be
considered usable.

[^past-foibles]:
    In the past we reused the single module and made changes in place. This
    happened to work out, but if something catastrophic had happened, and we
    needed to deploy the current cluster from scratch again, we would have had
    our work cut out for us, juggling reverts and likely Terraform state issues.
    This comes down to the fact that our Elasticsearch module is inflexible,
    with configuration created inside the module, rather than defined at the
    root module level. Because it's simpler to duplicate the module rather than
    add conditionals inside the module to handle multiple versions, the
    recommendation is to duplicate it. This ensures that we can redeploy the
    current cluster, whether entirely or just a failed node, without needing to
    juggle changes to the code configuring that cluster.

Deploy a staging cluster first. Production will come later. The cluster boxes
are expensive, so minimising the length of time that we have multiple cluster
versions deployed per environment helps save us some money and makes the list of
EC2 boxes a little less confusing to navigate.

```{warning}
The existing clusters will be deprovisioned at the end of the process and
should be left alone in the meantime. They are still being used by staging
and production until the final steps!
```

#### 5. Run a reindex with the new staging cluster

Update the staging ingestion server to use the new cluster (requires a staging
deployment) and manually trigger a `REINDEX` job, followed by
`CREATE_AND_POPULATE_FILTERED_INDEX`. Confirm index settings and mappings are as
expected and that the new documents are retrievable.

#### 6. Point the staging API to the new cluster

Update the staging API configuration to use the new cluster. Confirm the API is
stable and search works as expected.

#### 7. Deploy the new production cluster

Deploy the new production cluster. This should only require adding a reference
to the new Elasticsearch module in the production root module.

#### 8. Run a data refresh with the new production cluster

Point Airflow and the production ingestion server to the new cluster and run a
full data refresh, including any related DAGs like filtered index creation.
Confirm this works. Do not proceed until we are 100% confident the new cluster
works as expected. If in doubt, re-run the data refresh and make changes until
we are confident everything works perfectly.

#### 9. Point the production API to the new cluster

Update the production API configuration to use the new cluster. Confirm the API
is stable and search works, etc.

#### 10. Upgrade client versions, if necessary

If the client versions were not upgraded in
[step 2](#2-upgrade-the-client-version-if-necessary), upgrade them now and
deploy all updated services through to production. Confirm the data refresh
works before proceeding to the new step.

#### 10. Celebrate and deprovision the old clusters

Congrats! We should now be on the new Elasticsearch version. We can tear down
the old clusters and say goodbye to that Elasticsearch version. Be sure to
update CI to remove tests against the previous version as well. Reflect on this
process and identify potential improvements. Please update documentation to help
clarify pain-points or any pitfalls identified during the upgrade so that we are
better prepared the next time.

## Configuration changes

```{tip} How to choose which process to use
If the configuration change is needed to handle a security vulnerability
(e.g., `log4j`, etc), use the in-place approach. If the configuration change
is relatively minor, also use the in-place approach.

Otherwise, prefer to use the new cluster approach, as it is more robust and
has more opportunities to recover cleanly if something goes wrong.
```

### In place changes to live nodes

Elasticsearch nodes can be restarted one-by-one without issue. They will drop
from the cluster and once they are back up the will re-register themselves with
the cluster. This can be done at any time and should be okay. However, if it's
possible to time this during a period when indexing is not happening, that is
ideal. For severe security issues, of course, just go ahead and do it.

**Follow this process for the staging cluster first. After confirming that
cluster is okay, repeat for production.** If the changes only apply to
production then ignore this, but **_go slowly_**!

```{warning}
Be aware that this process requires modifying files via text-based editors
like `vim` or `nano`. If you are not comfortable with that process and
confident in how to use these editors, **do not attempt this process
yourself**. Find someone to buddy with you who can drive during the file
editing process.
```

1. Describe the specific configuration changes we need to make to each node. If
   we are modifying an existing configuration variable, document the existing
   setting and the new setting. If we are adding or removing a setting, document
   it! We need to make sure the existing configuration is as easy as possible to
   return to if the new configuration does not work as expected.
1. Log into AWS and go to the EC2 dashboard and filter the instances to list
   only the Elasticsearch nodes for the environment being modified.
1. Connect Elasticvue to the cluster and open the "Nodes" tab.
1. Open the CloudWatch API dashboard for the environment you are modifying and
   the Elasticsearch dashboard when making changes to the production cluster.
1. For each node, one-by-one, without concern for the order, do the following:
1. Note the instance identifier in a document accessible to other Openverse
   maintainers. Mark the node as started in the document.
1. Use the
   [EC2 Instance Connect feature](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-connect-methods.html#ec2-instance-connect-connecting-console)
   to connect to the node.
1. `cd /` and `ls` to confirm you can see the `docker-compose.yml`. This is the
   configuration file for the node.
1. Run `vim` or `nano` with `sudo` to edit the `docker-compose.yml` and make the
   configuration changes identified in the first step of the overall process.
1. Save the changes.
1. Run `docker-compose up -d` to restart the node with the new settings.
1. Mark the node as restarted in the shared document.
1. Monitor the cluster:

   - Confirm in Elasticvue that the node dropped from the cluster and wait for
     it to reappear and become stable[^health-during-refresh].
   - Check the CloudWatch dashboards and confirm everything remains stable or,
     if there are slight changes corresponding to the node dropping out, that
     metrics stabilise once the node has reinitialised.

1. Mark the node as completed in the shared document.
1. Do one last stability check for the environment's API and cluster.
1. Update the Terraform configuration to reflect the changes made to the live
   nodes.

That's it! Repeat the process for each relevant environment and open a PR for
the Terraform changes.

[^health-during-refresh]:
    If a data reindex is running then the cluster will probably report its
    health as "yellow". You should check that the node has reconnected and that
    its shards and replicas look good.

### Changes requiring a new cluster deployment

This process follows the same process outlined in
[version upgrades](#version-upgrades). That is, it is entirely likely that we
can treat the new configuration changes identically to a version upgrade, even
if the actual cluster version is not changing. If the cluster version is staying
the same and only configuration changes are being made, you can generally skip
reading release notes or confirming whether the client version is compatible,
etc. The main focus should be understanding the new configuration and
determining whether it's possible to test it locally. Otherwise, follow the
steps for deploying a new cluster and switching the live services over to it.

## Potential improvements

- Pass node configuration at the module level rather than generating it inside
  the module. This will enable using the same Elasticsearch module rather than
  needing to create a new one for each version.
- Use an auto-scaling group to deploy the nodes rather than creating each node
  individually.
- Use a single "current" endpoint to represent the "current" ES version and
  point all services to it. Rather than redeploying services with a new
  endpoint, use a load balancer to change the target ASG for the "current"
  endpoint. If services become unstable, just switch the target back to the old
  cluster, rather than needing to redeploy again.

# Deployment runbook

## Setup

1. Check [the running DAGs](https://airflow.openverse.org/home?status=running)
   in Airflow to make sure no DAGs are running.

   ```{caution}
   It is possible to perform a deploy if the image and audio refresh DAGs are
   running, but only if they are currently waiting on an `HttpSensor` step. If
   that is the case, you should pause the DAG, complete the deploy, and then
   unpause it back.
   ```

1. [Publish the drafted catalog release in the GitHub release page of the monorepo](https://github.com/WordPress/openverse/releases?q=catalog-)
   - Here you can preview the changes included in the catalog release and decide
     whether a release is necessary and adjust monitoring during the deployment
     accordingly.

## Deployment

The catalog only exists in production, so there is no staging deployment. After
the app is built and tagged, deploy production:

1. Checkout the
   [infrastructure repository](https://github.com/wordpress/openverse-infrastructure)
   and bump the catalog version with the `just bump production airflow` command.
1. `just ansible/playbook production airflow.yml -t airflow` and verify the plan
   before deploying. Unless configuration variables are changing along with the
   docker image version, the only change should be to the docker image tag in
   the compose file. Run the playbook with `-e airflow_apply=true` to instruct
   the playbook to actually apply any changes.

- If _any_ DAGs are running, the playbook will not apply the changes and will
  let you know that. If this happens, visit Airflow and confirm the list of
  running DAGs. If they can be stopped, stop them. If they need to be waited
  for, wait until they are done, then run the playbook again. If you must deploy
  and cannot wait for the DAGs to finish (or, if they are deferred and cannot
  finish), run the playbook with `-e airflow_force=true` to ignore the running
  DAGs check.
- See the [setup](#setup) section above for more information about when to
  decide if it is okay to deploy when DAGs are running.

## Post-deployment steps

1. Check for any Sentry errors in the maintainer's `#openverse-alerts` channel,
   or in the Sentry UI.
1. Ensure that Airflow is accessible at <https://airflow.openverse.org>.
1. If an Airflow version upgrade was deployed, ensure that the version is
   correct in the Airflow UI (bottom left of the footer on any page).
1. Review and Approve the automatically-generated changelog pull request in the
   repository.
1. Push up a PR to the infrastructure repository with the Ansible group var
   changes you pushed.
1. In the event of errors or problems, rollback the application by running the
   appropriate deployment workflow from the WordPress/openverse-infrastructure
   repository using the tag of the latest stable version. You can find the
   release version number in the [changelogs](/changelogs/index), and then the
   tag to pass to the action is the version number prefixed with "rel-", for
   example "rel-2023.07.03.17.52.00".
1. If anything else goes wrong or service is disrupted, consider this a
   Production Incident and notify the team.

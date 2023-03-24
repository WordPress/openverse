# Quickstart guide

This is the quick start guide for setting up and running the frontend locally.

## Prerequisites

Refer to the [general setup guide](../general_setup.md) for setting up the
prerequisites. Refer to the 'Frontend' column in the
[requirement matrix](../general_setup.md#requirement-matrix) to know what you
need to run this.

## Steps

1. Ensure you download, install and set up all prerequisites. Ensure that the
   Docker daemon is running.

2. Clone the repository to your computer. Then switch to the cloned directory.
   If you're planning to contribute, fork the repo and clone your fork instead.

   ```console
   $ git clone https://github.com/WordPress/openverse.git # or your fork
   $ cd openverse/
   ```

   If you followed the general setup guide and installed
   [GitHub CLI](./general_setup.md#github-cli), you can clone more simply using
   the `gh` command.

   ```console
   $ gh repo clone WordPress/openverse # or your fork
   $ cd openverse/
   ```

3. Install only the Node.js dependencies. You do not need to install any Python
   dependencies to run the frontend.

   ```console
   $ just node-install
   ```

4. Bring up the Docker services needed by the frontend. This includes Plausible
   and the PostgreSQL and Clickhouse databases it needs. Once this is done, you
   should be able to see the Plausible UI on
   [http://localhost:50288](http://localhost:50288).

   ```console
   $ just frontend/up
   ```

   The `frontend/up` recipe orchestrates the following services: `plausible_ch`,
   `plasible_db` and `plausible`.

5. To bring up the frontend, we have another `just` recipe. We have `just`
   recipes for almost everything. You can open
   [http://localhost:8443](http://localhost:8443) in a browser to see your very
   own copy of Openverse.

   ```console
   $ just frontend/run dev
   ```

   If you want your frontend to use a different API instance, you can set the
   `API_URL` environment variable to point to that instance. If you had the
   [API running locally](../api/quickstart.md), you can do the following to use
   the local API with the frontend.

   ```console
   $ env API_URL="http://localhost:50280" just frontend/run dev
   ```

   Once this step completes, you can be assured that the frontend is working
   fine.

6. You can <kbd>Ctrl</kbd> + <kbd>C</kbd> to terminate the frontend process.
   Then use another `just` recipe to bring down all the services. If you include
   the `-v` flag, it'll remove all volumes too.

   ```console
   $ just down
   $ just down -v # delete Docker volumes
   ```

7. To see the logs for all services, you can use the `logs` recipe. To see the
   logs for a particular service, pass the service name as an argument.

   ```console
   $ just logs
   $ just logs plausible # only see logs for Plausible
   ```

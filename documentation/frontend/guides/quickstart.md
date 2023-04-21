# Quickstart guide

This is the quick start guide for setting up and running the frontend locally.

## Prerequisites

Refer to the [general setup guide](/general/general_setup.md) for setting up the
prerequisites. Refer to the 'Frontend' column in the
[requirement matrix](/general/general_setup.md#requirement-matrix) to know what
you need to run this.

## Starting up

1. Ensure you download, install and set up all prerequisites. Ensure that the
   Docker daemon is running.

2. Clone the repository to your computer. Then switch to the cloned directory.
   If you're planning to contribute, fork the repo and clone your fork instead.

   ```console
   $ git clone https://github.com/WordPress/openverse.git # or your fork
   $ cd openverse/
   ```

   If you followed the general setup guide and installed
   [GitHub CLI](/general/general_setup.md#github-cli), you can clone more simply
   using the `gh` command.

   ```console
   $ gh repo clone WordPress/openverse # or your fork
   $ cd openverse/
   ```

3. Install only the Node.js dependencies. You do not need to install any Python
   dependencies to run the frontend.

   ```console
   $ just node-install
   ```

4. To bring up the frontend, we have another `just` recipe. We have `just`
   recipes for almost everything.

   ```console
   $ just frontend/run dev
   ```

   If you want your frontend to use a different API instance, you can set the
   `API_URL` environment variable to point to that instance. If you had the
   [API running locally](/api/guides/quickstart.md), you can do the following to
   use the local API with the frontend.

   ```console
   $ env API_URL="http://localhost:50280" just frontend/run dev
   ```

   Now you should be able to access the following endpoints:

   - the Openverse search engine frontend on
     [http://localhost:8443](http://localhost:8443)

## Shutting down

You can press <kbd>Ctrl</kbd> + <kbd>C</kbd> to terminate the frontend process.

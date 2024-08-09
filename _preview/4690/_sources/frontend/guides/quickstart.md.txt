# Frontend quickstart guide

This is the quick start guide for setting up and running the frontend locally.

## Prerequisites

Follow the [general setup guide](/general/general_setup.md) to set up `ov`.

## Starting up

1. Install additional Node.js dependencies. You do not need to install any
   Python dependencies to run the frontend.

   ```bash
   ov just node-install
   ```

2. To bring up the frontend, we have another `just` recipe. We have `just`
   recipes for almost everything.

   ```bash
   ov just frontend/run dev
   ```

   If you want your frontend to use a different API instance, you can set the
   `API_URL` environment variable to point to that instance. If you had the
   [API running locally](/api/guides/quickstart.md), you can do the following to
   use the local API with the frontend.

   ```bash
   ov env API_URL="http://localhost:50280" just frontend/run dev
   ```

   Now you should be able to access the following endpoints:

   - the Openverse search engine frontend on
     [http://localhost:8443](http://localhost:8443)

## Shutting down

You can press <kbd>Ctrl</kbd> + <kbd>C</kbd> to terminate the frontend process.

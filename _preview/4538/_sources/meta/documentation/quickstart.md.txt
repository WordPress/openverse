# Quickstart guide

This is the quick start guide for setting up and running the documentation
locally.

## Prerequisites

Follow the [general setup guide](/general/general_setup.md) to set up `ov`.

## Starting up

1. Install dependencies used by the documentation site:

   ```bash
   ov just documentation/install
   ```

1. Run the documentation live server. Once this is done, you should be able to
   see the documentation on [http://127.0.0.1:50230](http://127.0.0.1:50230).

   ```bash
   ov just documentation/live
   ```

   ````{admonition} Troubleshooting
   Sometimes, the documentation does not refresh to reflect changes in the table
   of contents or changes to the file system. In those cases, you can clean the
   caches and restart the live server.

   ```bash
   ov just documentation/clean
   ov just documentation/live
   ```
   ````

## Shutting down

You can press <kbd>Ctrl</kbd> + <kbd>C</kbd> to terminate the documentation live
server.

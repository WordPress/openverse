# Quickstart guide

This is the quick start guide for setting up and running the documentation
locally.

## Prerequisites

Refer to the [general setup guide](../general_setup.md) for setting up the
prerequisites. Refer to the 'Docs' column in the
[requirement matrix](../general_setup.md#requirement-matrix) to know what you
need to run this.

## Starting up

1. Ensure you download, install and set up all prerequisites.

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

3. Install only the Python dependencies. You do not need to install any Node.js
   dependencies to run the documentation.

   ```console
   $ just documentation/install
   ```

4. Run the documentation live server. Once this is done, you should be able to
   see the documentation on [http://127.0.0.1:50230](http://127.0.0.1:50230).

   ```console
   $ just documentation/live
   ```

   ````{admonition} Troubleshooting
   Sometimes, the documentation does not refresh to reflect changes in the table
   of contents or changes to the file system. In those cases, you can clean the
   caches and restart the live server.

   ```console
   $ just documentation/clean
   $ just documentation/live
   ```
   ````

## Shutting down

You can press <kbd>Ctrl</kbd> + <kbd>C</kbd> to terminate the documentation live
server.

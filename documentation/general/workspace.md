# Using workspaces

```{note}
This is an opinionated guide that only applies to VS Code users. If you use a
different editor or IDE, these instructions will not apply to you.
```

This is a guide to uses VS Code's multi-root workspace feature to work on
multiple sub-stacks of Openverse.

## Steps

1. Clone the GitHub repository.

   ```shell
   git clone --filter=blob:none https://github.com/WordPress/openverse.git # or your fork
   ```

1. In the same directory as the repository, create a workspace file
   `openverse.code-workspace` with the following configuration.

   ```json
   {
     "folders": [
       {
         "name": "monorepo",
         "path": "openverse"
       },
       {
         "name": "catalog",
         "path": "openverse/catalog"
       },
       {
         "name": "indexer_worker",
         "path": "openverse/indexer_worker"
       },
       {
         "name": "ingestion_server",
         "path": "openverse/ingestion_server"
       },
       {
         "name": "api",
         "path": "openverse/api"
       },
       {
         "name": "frontend",
         "path": "openverse/frontend"
       },
       {
         "name": "documentation",
         "path": "openverse/documentation"
       },
       {
         "name": "python/openverse-attribution",
         "path": "openverse/packages/python/openverse-attribution"
       }
     ],
     "settings": {
       "terminal.integrated.cwd": "${workspaceFolder:monorepo}"
     }
   }
   ```

1. From VS Code, open this workspace file. You should see the entire repository
   open in VS Code with all sub-stacks depicted as top-level folders.

   ![VS Code workspace](/_static/vs_code_workspace.png)

# API debugging guidelines

```{note}
This is an opinionated guide that only applies to VS Code users. If you use a
different editor or IDE, these instructions will not apply to you.
```

This is the guide to debugging the API using VS Code. This uses Microsoft's
`debugpy` package.

## Prerequisites

1. Install the
   [Python Debugger extension](https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy).
1. [Set up a VS Code workspace](/general/workspace.md) for the Openverse
   monorepo.

## Steps

1. Add a launch configuration to the Openverse workspace configuration. This
   configuration does the following things.

   - Specifies that the debugger used should be `debugpy`.
   - Configures the debugger to "attach" to a running process instead of
     launching a new one.
   - Specifies the port on which the `debugpy` server is running so that VS Code
     can connect to it.
   - Maps source code in the local repo clone to paths inside the Docker
     container so you can set breakpoints in the editor.

   ```json
   {
     // existing configuration
     "launch": {
       "version": "0.2.0",
       "configurations": [
         {
           "name": "API",
           "type": "debugpy",
           "request": "attach",
           "connect": {
             "host": "localhost",
             "port": 50256
           },
           "pathMappings": [
             {
               "localRoot": "${workspaceFolder:api}",
               "remoteRoot": "/api"
             }
           ],
           "justMyCode": true
         }
       ]
     }
   }
   ```

1. Edit the `compose.yml` file inside the `api/` directory to uncomment the
   `command` field and port mapping for port 5678.

1. Run the API server inside Docker using the instructions in the
   [quickstart](/api/guides/quickstart.md) guide.

1. Connect the debugger to the running instance from the Run and Debug panel.

   ![VS Code Run and Debug panel](/_static/vs_code_debug_panel.png)

1. Read the
   [Visual Code debugger's official instructions](https://code.visualstudio.com/docs/editor/debugging)
   to better understand how to use the debugger interface to accomplish tasks
   like setting breakpoints, watching variables etc.

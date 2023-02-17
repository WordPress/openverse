# Test

## Docker

1. Before running the tests, make sure to initialise the system with data.

   ```bash
   just init
   ```

   This step is a part of the {doc}`"Quickstart" <./quickstart>` process.

2. Run the tests in an interactive TTY connected to a `web` container.
   ```bash
   just api/test
   ```

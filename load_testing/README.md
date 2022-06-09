# Load testing

This directory contains a collection of locust files for load testing the Openverse application. Currently, only an API load test exists but in the future we can also create load tests for the frontend or any other service we stand up. These exist in this repository rather than one of the service specific ones for this reason. The setup for locust workers is tedious and by putting it here we can share utilities (like the dictionary one) and configuration boilerplate between load testing scripts for all our services. In the future it may also allow us to compose more complicated load tests that simulate things like our frontend and API both simultaneously being used in the same stack.

**Note:** Production is throttled, so these scripts cannot be used as a shortcut to DDoS our production stack.

## Running the tests

All load tests are accessible through `just` scripts in this directory's `justfile`.

To run API load tests against a local API instance, use `just api`. You can optionally specify a specific host and any other arguments to pass to locust. For example `just api https://api-dev.openverse.engineering -t 10m` will run the load tests against the staging API for 10 minutes.

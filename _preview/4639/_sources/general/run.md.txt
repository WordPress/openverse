# Run

## Service

### Docker

To run the API inside Docker, follow the instructions in the
[general setup guide](/general/general_setup.md).

### On the host

#### Prerequisites

- [Pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)

#### Steps

1. Create environment variables from the stencil file.

   ```bash
   ov just env
   ```

2. Install Python dependencies.

   ```bash
   ov just install
   ```

3. Start the Django dev server.
   ```bash
   ov just api/dj runserver
   ```

## Django admin

You can view the custom administration views at the `/admin/` endpoint. You can
use the username 'deploy' and password 'deploy' to log in.

## Configuration

All configuration is performed through environment variables. See the
`env.template` file for a comprehensive list of all environment variables. The
ones with sane defaults have been commented out.

- Pipenv will automatically load `.env` files when running commands with
  `pipenv run`.
- Docker Compose will automatically load `.env.docker` files inside the
  container.

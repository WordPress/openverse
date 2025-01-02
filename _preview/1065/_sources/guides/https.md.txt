# Testing HTTPS

To emulate the proxying behavior of production, we have set up an NGINX proxy
that serves the API over `https` by proxying to the Gunicorn server which serves
over `http`.

This proxy uses certificates from the `nginx/certs/` directory. These
certificates can be generated using `mkcert` with the `just nginx/cert` command.

Additionally, to test with the dev hostname `dev.openverse.test`, add the
following line to your hosts file.

```text
127.0.0.1 dev.openverse.test
```

Visiting `http://dev.openverse.test:9080` in your browser should permanently
redirect you to `https://dev.openverse.test:9443`.

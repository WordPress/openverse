# Nuxt Healthcheck

The Nuxt frontend's healthcheck is extremely naive. It confirms only that the
Nuxt server is running and able to respond to requests. It does not confirm
whether any required services are available (like the API) or whether rendering
is possible.

The Nuxt frontend's healthcheck can fail for the following reasons:

- The Nuxt server is unable to start and therefore unable to service requests
- The Nuxt server is overloaded and crashes while servicing the healthcheck
  request

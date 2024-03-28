# Logging

Openverse is in the process of establishing and implementing its logging
strategy. Until the
[introduction of more extensive logging in the Elasticsearch controller modules](https://github.com/WordPress/openverse-api/pull/790)
we did not have an established approach to logging. That PR still does not
establish a comprehensive approach, but it does introduce and follow some rules:

1. Always use a child logger based on the module name and method name. For
   example, at the top level of a module, there should be a `parent_logger`
   variable that is the result of calling `logging.getLogger(__name__)`.
   Individual methods that log should
   [get a child logger for themselves based on this parent logger and their method name](https://docs.python.org/3/library/logging.html#logging.Logger.getChild):

```py
def apply_filters(self, ...):
    logging = parent_logger.getChild("apply_filters")
    ...
```

2. When logging variable values, log them in the following format: `name=value`.
   Prefer that `name` equals the expression that produces the `value`. For
   example, if logging the length of a list named `providers`, `name` should be
   `len(providers)`, with the full expression looking like this:
   `len(providers)={len(providers)}`. If logging a property of an object, prefer
   `object.property_name={object.property_name}`. Exclude serialization from the
   name like `json.dumps` as this is assumed: `verified={json.dumps(verified)}`.
3. Avoid using the `pprint` module for serializing log data as it significantly
   increases the amount of space and time it takes to write a log. Instead,
   prefer a simpler `json.dumps`.

These practices provide context in the logs and makes them uniformly searchable
and filterable based on the values assigned to the names. Using a child logger
means we can easily see all the logs for a method. Using the `name=value` format
means we always know how to filter any given logged variable either by name or
by name and value.

Openverse also makes use of request IDs. Because multiple workers are writing to
the same log at once, any given request's logs may be interspersed with the logs
of another. Filtering on the request ID allows us to see the full logging story
of a single request. This allows us to trace problematic requests through the
codebase and understand what specific parts of the code are causing problems
with these particular requests.

## Future improvements

Potential future improvements to logging in Openverse could include:

1. Structured logging format like formatting all logs as JSON.
2. Establishing clearer practices around what log levels to use and when.

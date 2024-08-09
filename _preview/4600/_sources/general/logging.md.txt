# Logging

Openverse uses structured logging for the API.

## Best practices

We follow these guidelines when writing logs from the API.

1. Always declare the logger at the module level. This should ideally always be
   the same statement:

   ```python
   import structlog
   logger = structlog.get_logger(__name__)
   ```

   Consistently use the variable name `logger`, invoke `structlog.get_logger`
   (not `structlog.getLogger`) and supply `__name__` as the argument.

2. There is no need to define child loggers because structured logs will always
   include the `filename`, `funcname` and `lineno` fields.

3. When logging multiple fields, you can include them as keyword arguments to
   the logger. There is no need to serialize them or dump them as JSON. This
   allows `structlog` to automatically render them as appropriate.

   ```python
   logger.info("Event name", key_one=value_one, key_two=value_two)
   ```

Thanks to structured logging and uniform practices, our logs will be uniformly
searchable and filterable. For example, to see all the logs for a method and
only that method, one can pipe the logs through `grep` like so.

```bash
./ov just logs web | grep 'func_name=<function name>'
```

## Request IDs

Openverse also makes use of request IDs. Because multiple workers are writing to
the same log at once, any given request's logs may be interspersed with the logs
of another. Filtering on the request ID allows us to see the full logging story
of a single request. This allows us to trace problematic requests through the
codebase and understand what specific parts of the code are causing problems
with these particular requests.

```bash
./ov just logs web | grep 'request_id=<request ID>'
```

## Future improvements

Potential future improvements to logging in Openverse could include:

1. Establishing clearer practices around what log levels to use and when.

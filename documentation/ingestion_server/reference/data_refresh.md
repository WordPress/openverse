# Data Refresh Limit

The `DATA_REFRESH_LIMIT` variable can be used to define a limit to the number of
rows pulled from the upstream catalog database. If the server is running in an
`ENVIRONMENT` that is not `prod` or `production`, this is automatically set to
100k records.

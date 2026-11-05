# Safety and Security Considerations

The server has been designed to fail gracefully in the event of network
interruptions, full disks, etc. If a task fails to complete successfully, the
whole process is rolled back with zero impact to production.

The server is designed to be run in a private network only. You must not expose
the private Ingestion Server API to the public internet.

# Openverse API

The API has two sets of documentation.

- [Developer docs](https://wordpress.github.io/openverse-api/)

  - are focused towards developers who are building the Openverse API
  - can be seen locally by
    - running the following recipe:
      ```bash
      just sphinx-live
      ```
    - visiting the `https://localhost:50230/` endpoint
  - contain more details on how to contribute to the API project

- [Consumer docs](https://api.openverse.engineering/)
  - are focused towards consumers who are using the Openverse API
  - can be seen locally by
    - running the API service
      ```bash
      just up
      ```
    - visiting the `https://localhost:8000/` endpoint
  - contain more details about the API endpoints with usage examples

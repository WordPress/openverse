<img src="brand/banner.svg" width="100%"/>

<p align="center">
  <a href="https://github.com/orgs/WordPress/projects/3">Project Board</a> |
  <a href="https://make.wordpress.org/openverse/">Community Site</a> |
  <a href="https://make.wordpress.org/chat/">#openverse @ Slack</a> |
  <a href="https://make.wordpress.org/openverse/handbook/openverse-handbook/">Handbook</a> |
  <a href="https://make.wordpress.org/design/handbook/">Design Handbook</a> |
  <a href="https://www.figma.com/file/w60dl1XPUvSaRncv1Utmnb/Openverse-Releases?node-id=0%3A1">Releases mockups</a> |
  <a href="https://www.figma.com/file/GIIQ4sDbaToCfFQyKMvzr8/Openverse-Design-Library?node-id=0%3A1">Design Library</a>
</p>

<p align="center">
  Openverse is a search engine for openly-licensed media.
</p>

# Openverse

Openverse is a powerful search engine for GPL-compatible images, audio, and
more. Openverse is live at [openverse.org](https://openverse.org).

This repository contains most of the codebase, except for the Openverse catalog.
Eventually the catalog will be merged into this repository as well.

- [Catalog](https://github.com/wordpress/openverse-catalog) | The Apache
  Airflow-powered system for downloading and storing Openverse's metadata
- [Ingestion server](ingestion_server/) | The mechanism for refreshing the data
  from the catalog to the API
- [API](api/) | The Django REST API for querying the database, used by the
  frontend
- [Frontend](frontend/) | The public search engine at
  [openverse.org](https://openverse.org), built with Vue and Nuxt
- [Automations](automations/) | Scripts used for various workflows around
  Openverse repositories and processes

This repository also contains the following directories.

- [Brand](brand/) | Brand assets for Openverse such as logo and icon and
  guidelines for using these assets
- [RFCs](rfcs/) | Proposals and planning documents for discussing changes to
  Openverse
- [Templates](templates/) | Common scaffolding code that is rendered and synced
  to the catalog repo

## Contributing

For information on how to start contributing to Openverse please read the
[`CONTRIBUTING.md`](./CONTRIBUTING.md) document. You can look at some
[good first issues](https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3AWordPress%2Fopenverse-catalog+repo%3AWordPress%2Fopenverse+repo%3AWordPress%2Fopenverse-api+repo%3AWordPress%2Fopenverse-frontend+label%3A%22good+first+issue%22+label%3A%22help+wanted%22+-label%3A%22%E2%9B%94+status%3A+blocked%22+-label%3A%22%F0%9F%94%92+staff+only%22+)
to get started.

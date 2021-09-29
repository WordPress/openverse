<img src="brand/banner.svg" width="100%"/>

<p align="center">
  <a href="https://github.com/orgs/WordPress/projects/3">Project Board</a> | <a href="make.wordpress.org/openverse/">Community Site</a> | <a href="https://make.wordpress.org/chat/">#openverse @ Slack</a> | <a href="https://make.wordpress.org/openverse/handbook/openverse-handbook/">Handbook</a> | <a href="https://www.figma.com/files/project/31962071/Openverse?fuid=979162431688906882">Figma</a>
</p>

<p align="center">
  Openverse is a search engine for openly-licensed media.
</p>
  
# Openverse

Openverse is a powerful search engine for GPL-compatible images, audio, and more. Openverse is live at <a href="https://wordpress.org/openverse">wp.org/openverse</a>. 

This repository **does not** contain most of the codebase. The code is divided
into individual repositories, and managed via a
[GitHub Project Board](https://github.com/orgs/WordPress/projects/3):

- [Frontend](https://github.com/wordpress/openverse-frontend) | The public search engine at <a href="https://wordpress.org/openverse">wp.org/openverse</a>, built with Vue.js and Nuxt.js
- [Catalog](https://github.com/wordpress/openverse-catalog) | The Apache Airflow-powered system for downloading and storing Openverse's metadata
- [API](https://github.com/wordpress/openverse-api) | The Django REST API for querying the catalog data, used by the frontend
- [Browser extension](https://github.com/wordpress/openverse-browser-extension) | An extension to view Openverse images directly in your web browser

It is possible we will explore a monorepo structure in the future, but since all
the repos are decoupled from each other and use different technologies, we've
felt it best to keep them distinct.

## Contributing

Pull requests are welcome! Feel free to
[join us on Slack](https://make.wordpress.org/chat/) and discuss the project
with the engineers and community members in the #openverse channel.

You can also keep in touch with
[progress](https://github.com/orgs/WordPress/projects/3) and the latest updates
to the project with our
[WordPress contributor group](https://make.wordpress.org/openverse/).

### Helpful links for new contributors

- [Good first issues](https://github.com/search?q=label%3A%22good+first+issue%22+state%3Aopen+is%3Aissue+repo%3Awordpress%2Fopenverse+repo%3Awordpress%2Fopenverse-frontend+repo%3Awordpress%2Fopenverse-api+repo%3Awordpress%2Fopenverse-catalog+label%3A%22good+first+issue%22+state%3Aopen+repo%3Awordpress%2Fopenverse&type=Issues)
- [Openverse handbook](https://make.wordpress.org/openverse/handbook/openverse-handbook/)

## What *is* in this repo, then?

- This repo contains automation scripts used for various workflows around
  Openverse repositories and processes.
- It acts as the top-level meta repository for Openverse project where
  cross-repo discussions, issues and milestones are defined.
- It is the source of truth for repository meta-files such as common workflows,
  and issue and PR templates.
- It also contains brand assets like logo and icon, along with color and usage
  guidelines for the same.

## Repository structure

- **`python/`:** This directory contains scripts written in Python.
  - Use this as the working directory when executing Python scripts.
  - Requires [Pipenv](https://pipenv.pypa.io) as the package manager.

- **`js/`:** This directory contains scripts written in JavaScript.
  - Use this as the working directory when executing JavaScript scripts.
  - Requires [npm](https://www.npmjs.com) as the package manager.

- **`brand/`:** This directory contains brand assets for the project.

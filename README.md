# Openverse

Openverse is a search engine for openly-licensed media.

This repository **does not** contain most of the codebase. The code is divided
into three primary repositories, and managed via a
[GitHub Project Board](https://github.com/orgs/WordPress/projects/3):

- [Front-end](https://github.com/wordpress/openverse-frontend)
- [Catalog](https://github.com/wordpress/openverse-catalog)
- [API](https://github.com/wordpress/openverse-api)
- [Browser extension](https://github.com/wordpress/openverse-browser-extension)

It is possible we will explore a monorepo structure in the future, but as all
the repos are decoupled from each other and use different technologies, we've
felt it best to keep them distinct.

## Contributing

Pull requests are welcome! Feel free to
[join us on Slack](https://make.wordpress.org/chat/) and discuss the project
with the engineers and community members on #openverse.

You can also keep in touch with
[progress](https://github.com/orgs/WordPress/projects/3) and the latest updates
to the project with our
[WordPress contributor group](https://make.wordpress.org/openverse/).

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

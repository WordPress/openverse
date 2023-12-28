<a href="https://openverse.org">
  <img src="brand/banner.svg" width="100%" alt="Visit Openverse.org"/>
</a>

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

- [Catalog](catalog/) | The Apache Airflow-powered system for downloading and
  storing Openverse's metadata
- [Ingestion server](ingestion_server/) | The mechanism for refreshing the data
  from the catalog to the API
- [API](api/) | The Django REST API for querying the database, used by the
  frontend
- [Frontend](frontend/) | The public search engine at
  [openverse.org](https://openverse.org), built with Vue and Nuxt
- [Automations](automations/) | Scripts used for various workflows around
  Openverse repositories and processes
- [Utilities](utilities/) | Scripts or utilities which are useful across
  multiple projects or don't necessarily fit into a specific project.

This repository also contains the following directories.

- [Brand](brand/) | Brand assets for Openverse such as logo and icon and
  guidelines for using these assets
- [Templates](templates/) | Jinja templates that can be rendered into common
  scaffolding code for the project

## Keep in touch

You can keep in touch with the project via the following channels:

- GitHub
  - [Issues](https://github.com/WordPress/openverse/issues/)
  - [PRs](https://github.com/WordPress/openverse/pulls/)
  - [Discussions](https://github.com/WordPress/openverse/discussions/)
  - [Project Board](https://github.com/orgs/WordPress/projects/3)
- [Community Site](https://make.wordpress.org/openverse/)
- #openverse channel in the
  [Making WordPress Chat](https://make.wordpress.org/chat/)
  - Weekly Development Chat (@
    [Mondays 15:00 UTC](https://everytimezone.com/s/d2e71015))
  - Monthly Prioritisation Meeting (first Wednesday of every month @ 15:00 UTC)

## Documentation

To use the Openverse API, please refer to the
[API consumer documentation](https://api.openverse.engineering/v1/).

## Contributing

Pull requests are welcome! Feel free to
[join us on Slack](https://make.wordpress.org/chat/) and discuss the project
with the engineers and community members on #openverse.

You are welcome to take any open issue in the tracker labelled
[`help wanted`](https://github.com/WordPress/openverse/labels/help%20wanted) or
[`good first issue`](https://github.com/WordPress/openverse/labels/good%20first%20issue);
**there's no need to ask for permission in advance**. Other issues are open for
contribution as well, but may be less accessible or well-defined in comparison
to those that are explicitly labelled.

See the
[contribution guide](https://docs.openverse.org/general/contributing.html) for
details.

## Acknowledgments

Openverse, previously known as CC Search, was conceived and built at
[Creative Commons](https://creativecommons.org). We thank them for their
commitment to open source and openly licensed content, with particular thanks to
previous team members @ryanmerkley, @janetpkr, @lizadaly, @sebworks, @pa-w,
@kgodey, @annatuma, @mathemancer, @aldenstpage, @brenoferreira, and @sclachar,
along with their
[community of volunteers](https://opensource.creativecommons.org/community/community-team/).

Project proposal for
[Document all media properties](https://github.com/WordPress/openverse/issues/412)

## Due date:

2023-03-21

## Assigned reviewers

- [ ] @AetherUnbound
- [ ] @krysal

## Description

### Year Goal

Overcoming **Data Inertia**.

### Motivation

The first step in making the data we have reliable is describing it in detail.
Currently, we have more than 600 million rows of data about media in the catalog
database and similar but slightly different sets of data in the API database and
elasticsearch. Because of the history of the project, some data we have does not
conform to the requirements we now set and does not have the fields we describe
as required, and there are some fields that store a very different data piece
than what the users might expect[^1].

The main goal of this project is to establish a comprehensive baseline of our
media data: what information we currently have about each media item and what we
expect to have. Our database currently holds more than 700 million rows of media
data. The same data is in our API database and Elasticsearch, but the data
properties there are slightly different. Due to the project's history, some data
in the catalog does not meet our current requirements and lacks necessary
fields, while other fields store data that doesn't align with user
expectations[^1].

By documenting all data properties, we can ensure that we have a complete
understanding of the data. This documentation will improve the API user and the
Openverse maintainer experience. It will also be the basis for data
normalization which will lead to faster searches and a better experience for
catalog and API contributors, as well as API users.

### Success criteria

The project will be considered successful when the document described below is
created, reviewed by at least two maintainers, and published on the Openverse
documentation site.

### Implementors

@rwidom - creator of the
[image table](https://docs.google.com/spreadsheets/d/1gaVsvFnsYby2iwzRm0Ta9IPhvNixCpQdHByGLo1r_pg/edit?usp=sharing)
("image table ddl" tab)

@obulat - main implementor @openverse-team - reviewers

### Implementation details

As this is mainly a documentation project, its implementation plan can be
written here, inside the project plan. (I think splitting it will unnecessarily
slow down a smallish project. Please, correct me if you think I'm wrong) This
project will create a table with all the media properties that we store or
compute on all levels of the stack (Catalog, API database, API elasticsearch,
Frontend). This table will serve as a basis for any work on data normalization
work. As such, it will be a work in progress because the links to the code and
the details about the properties should change as we progress through the data
normalization project. We can publish it on the monorepo documentation site or
the Openverse blog on Make WordPress, with the admonition that the table is a
living document and will be updated.

The table will start with a list of columns in the Catalog database. For each
property, we will provide the following information:

- A clear definition of what the property represents.
- An explanation of where the property is sourced from in the catalog, and any
  special considerations that should be taken into account when extracting it.
  For instance, in the case of the `creator` field, we will specify whether to
  use the `author`, `photographer`, or both.
- The property's data type, and whether it is required or nullable. We will also
  indicate if the property is required but not present in some data, such as
  `license_url` in the `meta_data` field. If the property has a set of distinct
  values, we will note where they are in the code.
- Whether the property is served by the API, and if so, on which endpoints
  (search or single result, or both). We will also highlight any differences
  between the property's type in the API versus the catalog, as noted in the
  database, Elasticsearch, or API documentation.
- If the API does not take the data directly from the catalog database, we will
  indicate how the data is computed, and where this occurs (during data refresh,
  indexing, or as a fallback in the API). We will provide a link to the relevant
  code, if available.
- We will also document whether the property is used by the frontend, whether
  the type matches the catalog/API response type, and whether the frontend
  performs any cleanup or sanitization of the property. A link to the relevant
  code will be provided, if available.

#### Tools

The main tool to use for this table is an online spreadsheet app. I'm a little
uncertain of whether the amount of information would be too much to fit into one
table. If it is, it might be a good idea to split the data into a table with
more standard pieces of information, and a list of all data properties with
longer descriptions and things like code links and the criteria for selecting
data from provider APIs.

#### The process for updating the table

In the future, when the data is cleaned or changed in any way, we will need to
update the table accordingly. If we keep it in the documentation site, we can
use PRs to keep the history of changes, linking to all the related PRs.

#### Localization concerns

We should identify whether any pieces of data are translated or left as is, and
whether it might be necessary (and possible) to translate any pieces. There is
an [open issue](https://github.com/WordPress/openverse/issues/589) about
translating audio genres, for example.

### Infrastructural changes

None.

### Marketing outreach and outside stakeholders

I don't think we need the marketing outreach, but we will probably want to share
the table on the Make blog, and with the teams that work with the API (like
Gutenberg contributors)

[^1]:
    Recent example is the `created_on` field, which actually stores the
    timestamp when the media was first indexed in Openverse, and not when the
    particular media item was created. This was uncovered in a
    [PR to sort the search results based on the creation date](https://github.com/WordPress/openverse-api/pull/916).

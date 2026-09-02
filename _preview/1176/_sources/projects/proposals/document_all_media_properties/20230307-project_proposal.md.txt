Project proposal for
[Document all media properties](https://github.com/WordPress/openverse/issues/412)

## Due date:

2023-03-21

## Assigned reviewers

- [x] @AetherUnbound
- [ ] @krysal

## Description

### Year Goal

Overcoming **Data Inertia**.

### Motivation

The first step in making the data we have reliable is describing it in detail.
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

The project will be considered successful when:

- the documentation of all media properties is created, automatically extracted
  from the code where possible.
- the documentation is published on the Openverse documentation site, and the
  process for automatically updating or encouraging the maintainers to update it
  on relevant code changes is created.

### Implementors

@rwidom - creator of the
[image table](https://docs.google.com/spreadsheets/d/1gaVsvFnsYby2iwzRm0Ta9IPhvNixCpQdHByGLo1r_pg/edit?usp=sharing)
("image table ddl" tab)

@obulat - main implementor @openverse-team - reviewers

### Implementation details

The scope of this project was increased from creating a markdown table
documenting all the media properties on all levels of the stack (Catalog, API
database, API elasticsearch, Frontend) to adding automation to update it and
generating as much documentation as possible to the documentation that lives
next to the code. This means that the project will need the implementation plan.

#### Table as a living document

This table will serve as a basis for any work on data normalization work. As
such, it will be a work in progress because the links to the code and the
details about the properties should change as we progress through the data
normalization project. To ensure that the table is up-to-date, this project will
also add automation to the catalog CI pipeline to detect changes to the fields
in the table and the catalog DDL and add a comment to update them, similar to
the
[migration safety warning](https://github.com/WordPress/openverse/blob/main/.github/workflows/migration_safety_warning.yml).

We will publish the table on the
[Openverse documentation site](https://docs.openverse.org/), with the admonition
that the table is a living document and will be updated.

#### Table contents

The table will start with a list of columns in the Catalog database. For each
property, we will provide the following structured data:

- The property's data type in the database, and whether it is required and/or
  nullable.
- The Python column that is used to represent the property when saving the TSVs.
- A short clear definition of what the property represents.

For each property, we will also provide the following information in free-form
text:

- An explanation of where the property is sourced from in the catalog, and any
  special considerations that should be taken into account when extracting it.
  For instance, in the case of the `creator` field, we will specify whether to
  use the `author`, `photographer`, or both.
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
- We will also indicate if the property is required but not present in some
  data, such as `license_url` in the `meta_data` field. If the property has a
  set of distinct values, we will note where they are in the code.

#### Tools

The table will be created by parsing the local catalog database DDL and the
Python code that is used to save the TSVs. We can use `ast` module to parse the
files and extract the necessary information. The data about where the properties
are sourced from in the catalog will be extracted from the `MediaStore`,
`ImageStore` and `AudioStore` classes. To make it easier, we can change the
`add_item` function to take a dataclass with all the properties as arguments,
describe how to source each property from providers in the docstrings, and then
extract these docstrings into the markdown document. The API already creates an
OpenAPI schema, which we can enrich by adding the information for each property
of whether it is taken from the catalog "as is" or computed in the Django or the
Elasticsearch code. This OpenAPI schema will then be used to generate the types
for the Nuxt frontend, and also be extracted into the markdown document.

#### The process for updating the table

In the future, when the data is cleaned or changed in any way, we will need to
update the docstrings accordingly, and this will update the documentation.

#### Localization concerns

We should identify whether any pieces of data are translated or left as is, and
whether it might be necessary (and possible) to translate any pieces. There is
an [open issue](https://github.com/WordPress/openverse/issues/589) about
translating audio genres, for example.

#### Limitations for `meta_data` field

It will not be possible to document all the fields inside the `meta_data`
column. It is a JSON column that was used to collect "whatever doesn't fit in
the other fields" and its values can vary greatly. It would be extremely time-
and resource-consuming to try to extract _all_ available meta_data fields. For
this column, we will describe what we currently expect as a bare minimum value
for it, and also the meta_data fields that are used in the provider scripts

### Infrastructural changes

None.

### Marketing outreach and outside stakeholders

I don't think we need the marketing outreach, but we will probably want to share
the table on the Make blog, and with the teams that work with the API (like
Gutenberg contributors).

[^1]:
    Recent example is the `created_on` field, which actually stores the
    timestamp when the media was first indexed in Openverse, and not when the
    particular media item was created. This was uncovered in a
    [PR to sort the search results based on the creation date](https://github.com/WordPress/openverse-api/pull/916).

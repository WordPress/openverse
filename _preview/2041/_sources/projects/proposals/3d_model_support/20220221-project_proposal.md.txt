# 2022-02-21 Project Proposal: 3D model support

- [x] @sarayourfriend
- [x] @panchovm

## Rationale

The Openverse team and members of the community have identified a number of
sources of CC-licensed 3D models. We would like to add these models to
Openverse, as they can be useful for game development, art, 3D printing, etc. In
order to incorporate them into Openverse, we need to add a new media type and
provide infrastructure in the frontend for rendering the models.

## Overview

Openverse will add first-class support for 3D models, alongside audio and
images. This means 3D models will have their own table in the Catalog, and their
own API endpoints. Adding these to the frontend will require some new components
and utilities, but should be more straightforward than the implementation of
audio because we are not conducting a complete redesign of the site in parallel.

This outline of work is predicated on the idea that we've identified sources of
3D models and will seek to flesh out the details regarding metadata fields,
database migrations, API development, and frontend work.

This work describes 3D models as a specific entity, exclusive of 2D models. 2D
models can be covered under our `image` media type and identified via a separate
category.

## 3D Models in the Catalog & API

### Some potential risks

- As it stands currently, each new media type means an additional data refresh.
  Data refreshes cannot be run simultaneously at present, so we may reach a
  saturation point where all of our data cannot be refreshed weekly.
- We do not have any standard database migration approach for the catalog, so
  all changes suggested here will likely be ad hoc unless #235 is addressed
  prior to this implementation.
- The API, while it does have a migration tool, does not have a standardized
  migration application process. We will need to run the migration manually when
  the time comes.

### Some other considerations

- It would be ideal to have this under a feature flag in the API. We could
  perform deployments and testing on our staging setup with the flag enabled,
  but still make other deployments to production with the flag disabled. We
  should be able to run the API for images & audio successfully with the feature
  flag disabled AND without having run the migrations.
- As we work through this on both the catalog and the API, we should begin
  compiling information for a document describing the process for adding a **new
  media type**. This will be useful for future media types we are sure to add!

### Prior work

We may be able to use previous work regarding the addition of audio to the
catalog/API as a guide. These updates required a fair amount of generalization,
which we may not need to do a second time around.

https://github.com/wordpress/openverse/issues/19

### Design requirements

#### New content type

- [ ] Create a 3D model icon
- [ ] Create an icon indicating that the image is a 3d model screenshot/preview

#### Search results

- [ ] Add 3d model results in the All content results
- [ ] Design a 3d model results page
- [ ] Review and include filter components if necessary

#### Single result view

- [ ] Design the 3d model single view

### Technical implementation

#### 1. Add 3D models to the catalog

- [ ] Define necessary fields & schema for `model_3d` table & associated data
- [ ] Add DDL to local Postgres image:
      https://github.com/WordPress/openverse-catalog/tree/main/docker/upstream_db
- [ ] Create a popularity calculation view for `model_3d`
- [ ] Add the database columns to `db_columns.py`:
      https://github.com/WordPress/openverse-catalog/blob/main/openverse_catalog/dags/common/storage/db_columns.py
- [ ] Add the TSV columns to `tsv_columns.py`:
      https://github.com/WordPress/openverse-catalog/blob/main/openverse_catalog/dags/common/storage/tsv_columns.py
- [ ] Create a `Model3DStore` subclass of
      [`MediaStore`](https://github.com/WordPress/openverse-catalog/blob/9538f38401e5428b32dc14c5d5ba7ef50af87a96/openverse_catalog/dags/common/storage/media.py#L39):
- [ ] Update the
      [new provider API script template](https://github.com/WordPress/openverse-catalog/tree/main/openverse_catalog/templates)
      with the `model_3d` provider
- [ ] Create one/several provider API scripts & associated DAGs

#### 2. Add 3D models to the API

_Note: Borrowed heavily from https://github.com/wordpress/openverse/issues/19_

- [ ] Django models for `model_3d`
- [ ] Add DRF serializers for `model_3d`
- [ ] Add DRF endpoints for `model_3d`
- [ ] Make the thumbnail server work with model thumbnails

#### 3. Add 3D models to the data refresh

- [ ] Add Elasticsearch `model_3d` models
- [ ] Ensure the data refresh works for 3D models
- [ ] Add 3D model sample data into the sample data CSV for testing

### Open Questions

- What data is important to store in the catalog? Some of this is encapsulated
  in the proposed schema, but there may be other important attributes beyond
  those listed.
- Will it be important to differentiate the "type" of 3D model that a particular
  record refers to? (E.g. 3D printer model, game asset, artwork, etc.)
- Many model sites come with asset groups, should we have a table similar to
  `AudioSets` for these cases?

### Proposed schema

Below is the proposed schema for the `model_3d` table in the catalog database.
It is subject to change based on discussions that happen here and elsewhere.

Many of the fields towards the end are taken from examples on SketchFab (e.g.
https://sketchfab.com/3d-models/charmanders-midnight-snack-57866c01da20414ba81885206acbcc85)

| Field                     | Type        | Description                                                                                                        |
| ------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------ |
| `identifier`              | `UUID`      | Identifier for the record                                                                                          |
| `created_on`              | `timestamp` | Time the record was created                                                                                        |
| `updated_on`              | `timestamp` | Time the record was updated                                                                                        |
| `ingestion_type`          | `varchar`   | What generated the record                                                                                          |
| `provider`                | `varchar`   | Provider API that the model comes from                                                                             |
| `source`                  | `varchar`   | Source within the provider (e.g. NASA on Flickr), typically the same as `provider`                                 |
| `foreign_id`              | `varchar`   | Identifier that the provider uses for this model                                                                   |
| `foreign_landing_url`     | `varchar`   | URL on the provider that displays the "single-result" page for this model                                          |
| `url`                     | `varchar`   | URL to the actual asset itself (e.g. the image URL)                                                                |
| `thumbnail`               | `varchar`   | Thumbnail URL                                                                                                      |
| `filesize`                | `integer`   | Size of the file                                                                                                   |
| `license`                 | `varchar`   | License for the model                                                                                              |
| `license_version`         | `varchar`   | Version of the model's license                                                                                     |
| `creator`                 | `varchar`   | Creator ID of the model from the provider                                                                          |
| `creator_url`             | `varchar`   | URL to the creator's page on the provider's site                                                                   |
| `title`                   | `varchar`   | Title of the model                                                                                                 |
| `meta_data`               | `jsonb`     | Uncategorized metadata for the model                                                                               |
| `tags`                    | `jsonb`     | Tags that describe the model, for use in searching                                                                 |
| `watermarked`             | `bool`      | Whether the model is watermarked - is this needed for 3D models?                                                   |
| `last_synced_with_source` | `timestamp` | Time the record was last updated from the provider                                                                 |
| `removed_from_source`     | `bool`      | Whether the model has been removed from the upstream source                                                        |
| `category`                | `varchar`   | Category for the model (is this where we'll make the distinction between 3D printers, game assets, etc.?)          |
| `filetype`                | `varchar`   | File type of the primary file for the model                                                                        |
| `alt_files`               | `jsonb`     | Additional file types for the model                                                                                |
| `vertices`                | `integer`   | Number of vertices within the model                                                                                |
| `textures`                | `integer`   | Number of [textures](https://en.wikibooks.org/wiki/Blender_3D:_Noob_to_Pro/Materials_and_Textures) the model uses  |
| `materials`               | `integer`   | Number of [materials](https://en.wikibooks.org/wiki/Blender_3D:_Noob_to_Pro/Materials_and_Textures) the model uses |
| `uv_mapping`              | `bool`      | Whether the model contains [UV Mapping](https://en.wikipedia.org/wiki/UV_mapping)                                  |
| `vertex_colors`           | `bool`      | Whether the model contains [vertex colors](https://help.sketchfab.com/hc/en-us/articles/210765623-Vertex-Colors)   |
| `pbr`                     | `bool`      | Whether the model supports [physically based rendering](https://en.wikipedia.org/wiki/Physically_based_rendering)  |
| `rigged_geometries`       | `bool`      | Whether the model supports [rigging for animation](https://dreamfarmstudios.com/blog/what-is-3d-rigging/)          |
| `animations`              | `integer`   | Number of animations the model has                                                                                 |
| `morph_geometries`        | `integer`   | Number of [morph targets for animation](https://en.wikipedia.org/wiki/Morph_target_animation)                      |

## 3D Models in the frontend

### Some potential risks

#### Performance

3D models are often heavy files. We should lazy-load and defer loading of these
resources as much as possible. We should probably use _thumbnails_ rather than
actually render 3D models in the search results. We _could_ consider something
like
[SketchFab's search results](https://sketchfab.com/search?q=snacks&type=models),
where they render a 3D model on hover of the search results, when on desktop.

- We need to consider low power devices and low bandwidth connections. In both
  of these instances we'll want to try and significantly limit the number of
  downloaded assets. Some solutions for this might be:
  - Write new composables and/or components to detect user bandwidth and power
    (see https://github.com/GoogleChromeLabs/react-adaptive-hooks as an example
    in React!)
  - Only display thumbnails on list views
  - Have a 'play' button on single result views, that triggers the loading of
    code-split model viewer code
  - Simplify mobile models by default, by using flat colors instead of textures,
    limiting vertice counts, or other approaches. We need to research what is
    possible here, and what might give a user a false negative impression about
    a model. We don't want to inadvertently destroy someone's work to the point
    that users won't want to download it.

#### File types

- Likely formats to support:
  - [glTF](https://www.khronos.org/gltf/)
  - [fbx](https://docs.fileformat.com/3d/fbx/)
  - [Usdz](https://www.marxentlabs.com/usdz-files/)
  - [obj](https://all3dp.com/1/obj-file-format-3d-printing-cad/)
- We'll need to find a standardized 3d model viewer that will work with various
  formats. We _really, really_ don't want to write our own code here. We will
  also need to decide if we want to use this universally, or use SketchFab's
  viewer for SketchFab models, which is an excellent viewer.
  - [Trois](https://github.com/troisjs/trois) is a good candidate. This is a
    Vue3 renderer for ThreeJS.

### Prior Art

- We already show 3D models as
  [part of images](https://search.openverse.engineering/search/image?q=dogs&source=sketchfab,thingiverse),
  which is great! Fewer scripts to write on the catalog side.
  - To migrate these providers we should:
    - Update and modify the provider scripts to support our 3d model type
      instead of images
    - Purge their existing images from the catalog `image` database table.
    - Run the updated provider scripts.
- We also already show Sketchfab's 3D model viewer for their single results:
  https://search-staging.openverse.engineering/image/00a6a7a4-6605-4cba-bacf-a08b0da546b9

### Collaborators

- The
  [Open Metaverse Interoperability Group](https://github.com/omigroup/omigroup)
  aims to standardized protocols for interactive elements in 3D scenes. Core
  contributor @antpb is a part of this group.1
- Our friend @nebulousflynn at Sketchfab might have some ideas and suggestions
  as well.

### Some code considerations

- When a unique identifier is necessary, we should use the string constant
  `const MODEL_3D = '3d model'` to refer to 3D models. Compare this to `AUDIO`
  for audio files, for example.
- Similar to the catalog/API, 3D model support should be enabled via a feature
  flag. This work should be able to be committed directly to `main` without a
  base feature branch needed. Meta search support for 3D models does not need to
  be feature flagged.
- e2e tests should be added for any new routes; and updated for existing routes
  that are modified. PRs will be blocked in the abcense of these tests.
- New content types should always launch in `beta` until we reach a certain
  number of results and/or are confident in our UI components (this metric(s)
  need to be determined).
- Many of the todos identified here can be broken down into even smaller pieces
  in the future, particularly around the user interface.

### Technical implementation

#### 1. Add 3D Models to Meta Search

##### Prerequisites

- Need a list of 3D model providers to use in meta search. This could be a mix
  of sources we intend to use in the Catalog but also some that don't have APIs
  and will stay in meta search after launching 3D model support.

##### Todos

- [ ] Add 3D models to the content switcher components:
  - [ ] https://github.com/WordPress/openverse-frontend/blob/bbccc36ed49186b369cc4a69693fbc6d1411f29a/src/components/VContentSwitcher/VContentSwitcherButton.vue
  - [ ] https://github.com/WordPress/openverse-frontend/blob/7d74f033ddc4d35889d7c43756c36150beee4192/src/components/VContentSwitcher/VContentTypes.vue
- [ ] Create a `model/index.vue` endpoint for 3D models in the
      [pages directory](https://github.com/WordPress/openverse-frontend/blob/037f2efb768fdbdcff4b875e7f7c271ff50df59f/src/pages)
- [ ] Add 3D model sources to the
      [legacy sources lookup](https://github.com/WordPress/openverse-frontend/blob/268532a05004b72fb91b77a875f3a3c1d7fb0599/src/utils/get-legacy-source-url.js#L1)
- [ ] Add 3D models to the
      [media constants](https://github.com/WordPress/openverse-frontend/blob/4aeb9fd0d9f893f2df1752d6bb1e52351b8c3d35/src/constants/media.js#L13)
      file, making sure it is set to the `ADDITIONAL` status.

#### 2. Setup the data for 3D models

- [ ] Create a feature flag for 3D model support. All 3D model features will be
      behind this. _This specific implementation is waiting on a feature flag
      RFC and should be updated once that is finalized._
- [ ] Generate mock/sample api response data for 3D models.
- [ ] Create a new media service for Models in the
      [data directory](https://github.com/WordPress/openverse-frontend/blob/fe24ec9bf6a4d3ad429901cef53744dccd93ed5d/src/data)
- [ ] Update the
      [media constants](https://github.com/WordPress/openverse-frontend/blob/4aeb9fd0d9f893f2df1752d6bb1e52351b8c3d35/src/constants/media.js#L1)
      file with new constants for models, and under the `BETA` flag.
- [ ] Update the
      [media store](https://github.com/WordPress/openverse-frontend/blob/f9f549beace4f76480c8cbf1e91d8940a0aeef2b/src/store/media.js#L347)
      with 3D model support.

#### 3. Implement new 3D model UI

##### Prerequisites

Design work for the new components must be completed, or at least in a good
enough place that we decide work can begin.

##### Todos

- [ ] Add 3D models to the All Results view
  - [ ] Create a `VModelCell.vue` component in the
        [`VAllResultsGrid` directory](https://github.com/WordPress/openverse-frontend/blob/f5b7518c3942a2ede49d5c7fef2831d30e9867a9/src/components/VAllResultsGrid)
  - [ ] Add the logic to display models in the
        [`VAllResultsGrid.vue`](https://github.com/WordPress/openverse-frontend/blob/8214217f84099a83b9767f6a5c73fdbdf278bc95/src/components/VAllResultsGrid/VAllResultsGrid.vue#L1)
        component.
- [ ] Create a new single model route `pages/model/_id.vue` for viewing a 3D
      model in detail.
  - [ ] Render the model
  - [ ] Render the model info
  - [ ] Render the attribution information
  - [ ] Render the related models
- [ ] Create a new `VThreeDModel.vue` component that supports displaying 3D
      models of various file formats

### Open Questions

- What model formats do we want/need to support?
- What features do people need in a 3D model search engine? What functionality
  does our model viewer need to have?
- Should we use SketchFab's viewer for SketchFab models?
- Some models are meant to be 3D printed; some are meant to be used as assets in
  digital art and games; others are more like standalone pieces of artwork.
  There are probably different user stories for each of these types. How can we
  optimize our UI for all of these different experiences?

### Related RFCs

- Frontend Feature Flagging _Todo: Add link once created_
- API Feature Flagging _Todo: Add link once created_

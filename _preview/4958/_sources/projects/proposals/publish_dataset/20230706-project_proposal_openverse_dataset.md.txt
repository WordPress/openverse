# 2023-07-06 Project Proposal: Providing and maintaining an Openverse image dataset

```{attention}
The Openverse maintainer team has decided to pause this project for the time
being. [See our public update on it here](https://github.com/WordPress/openverse/issues/2545#issuecomment-1682627814).
This proposal may be picked back up when the discussion reopens in the future.
```

**Author**: @zackkrida

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @AetherUnbound
- [x] @sarayourfriend

## Project summary

This project aims to publish and regularly update a dataset or _datasets_ of
Openverse's media metadata. This project will provide access to the data
currently served by our API, but which is difficult to access in full and
requires significant time, money, and compute resources to maintain.

## Motivation

For this project, understanding "why?" we would do this is of paramount
importance. There are several key philosophical and technical advantages to
sharing this dataset with the public.

### Open Access + Scraping Prevention

Openverse is and always has been, since its days as
["CC Search"](https://creativecommons.org/2021/12/13/dear-users-of-cc-search-welcome-to-openverse/),
informed by principles of the open access movement. Openverse strives to remove
all all financial, technical, and legal barriers to accessing the works of the
global commons.

Due to technical and logistical limitations, we have previously been unable to
accessibly provide access to the full Openverse dataset. Today, users need to
invest significant time and money into scraping the Openverse API in order to
access this data. These financial and technical barriers to our users are deeply
inequitable. Additionally, this scraping disrupts Openverse access and stability
for all users. It also requires significant maintainer effort to identify,
mitigate, and block scraping traffic.

By sharing this data as a full dataset on
[HuggingFace](https://huggingface.co/datasets), we can remove these barriers and
allow folks to access the data provided by Openverse.org and the Openverse API
without restriction.

### Contributions Back to Openverse

Easily accessed Openverse datasets will facilitate easier generation of machine
labels, translations, and other supplemental data which can be used to improve
the experience of Openverse.org and the API. This data is typically generated as
part of the
[data preprocessing](https://huggingface.co/docs/transformers/preprocessing)
stage of model training.

Presence on HuggingFace in particular will enable community members to analyze
the dataset and create supplemental datasets; to train models with the dataset;
and to use the dataset with all of HuggingFace's tooling: the
[Datasets](https://github.com/huggingface/datasets) library in particular.

It is worth noting that this year we identified many projects to work on which
rely on bulk analysis of Openverse's data. These projects could be replaced by,
or made easier by the publication of the datasets. This could work in a few
ways. A community member, training a model using the Openverse dataset,
generates metadata that we want and planned to generate ourselves. Then, the
HuggingFace platform presents an alternative to other SaaS (software as a
service) products we intended to use to generate machine labels, detect
sensitive content, and so on. Instead of those offerings we use models hosted on
the HuggingFace hub. The
[Datasets library](https://huggingface.co/docs/datasets/index) allows for easy
loading of the Openverse dataset in any data pipelines we write. HuggingFace
also offers the ability to deploy production-ready API endpoints for
transformation models hosted on their hub. This feature is called
[Inference Endpoints](https://huggingface.co/docs/inference-endpoints/index).

#### Potentially-related projects

- [External API for sensitive content detection #422](https://github.com/WordPress/openverse/issues/422) -
  Instead of Rekognition or Google Vision, we may want to use a community model
  on HuggingFace.
- [Machine Image Labeling pipeline #426](https://github.com/WordPress/openverse/issues/426)
  Either a community member may create an up to date set of machine-generated
  labels we could use, or we could again create an Inference Endpoint with an
  existing model, for example
  [Vision Transformer](https://huggingface.co/google/vit-base-patch16-224)
- [Duplicate image detection #427](https://github.com/WordPress/openverse/issues/427) -
  Deduplication is an extremely common and important preprocessing step. It will
  surely be implemented by community contributors and can be reapplied to
  Openverse itself. It's possible we'll want a different deduplication strategy
  that considers provenance and ownership (i.e, did the original author upload
  or someone else), but at a minimum, we should be able to use community
  solutions to _identify_ duplicates.

### Resiliency

The metadata for openly-licensed media, used by Openverse to power the API and
frontend, is a community utility and should be available to all users,
_distinctly_ from Openverse itself. By publishing this dataset, we ensure access
to this data is fast, accessible, and resilient. With published datasets, this
access remains even if Openverse is inaccessible, under attack, or experiencing
any other unforeseen disruptions.

## Goals

<!-- Which yearly goal does this project advance? -->

This project encompasses all of our 2023 "lighthouse goals", but "Community
Development" is perhaps the broadest and most relevant. Others touched on here,
or impacted through potential downstream changes, are "Result Relevancy",
"Quantifying our Work", "Search Experience", "Content Safety", and "Data
inertia".

## Requirements

<!-- Detailed descriptions of the features required for the project. Include user stories if you feel they'd be helpful, but focus on describing a specification for how the feature would work with an eye towards edge cases. -->

This project requires coordination with HuggingFace to release the dataset on
their platform, bypassing their typical restrictions for Dataset size.

We will also need to figure out the technical requirements for producing the raw
dataset, which will be done in this project's implementation plan. Additionally
in that plan we will:

- Determine if we host a single dataset for all media types, or separate
  datasets for different media types.
- Develop a plan for updating the datasets regularly
- Refine how we will provide access to our initial, raw dataset for upload to
  HuggingFace. This refers to the initial, raw dump from Openverse, not the
  actual dataset which will be provided to users. These details are somewhat
  trivial as the data can be parsed and transformed prior to distribution.
  - Delivery mechanism, likely a requester pays S3 bucket
  - File format, likely parquet files

We will also need to coordinate the launch of these efforts and associated
outreach. See more about that in the [marketing section](#marketing).

## Success

<!-- How do we measure the success of the project? How do we know our ideas worked? -->

This project can be considered a success when the dataset is published. Ideally,
we will also observe meaningful usage of the dataset. Some ways we might measure
this include:

- Metrics built into HuggingFace
  - Models trained with the Dataset are listed
  - Downloads last month
  - Likes
- Our dataset trending on HuggingFace
- Additionally, we may also see increased interest in our repositories
- Any positive engagement with our marketing efforts for the project

## Participants and stakeholders

<!-- Who is working on the project and who are the external stakeholders, if any? Consider the lead, implementers, designers, and other stakeholders who have a say in how the project goes. -->

- Openverse maintainers - Responsible for creating the initial raw data dump,
  maintaining the Openverse account and Dataset on HuggingFace. We also need to
  make sure maintainers are protected from liability related the dataset, for
  example: from distributing PDM works, works acquired by institutions without
  consent or input from their cultures of origin, or copyrighted works
  incorrectly marked as CC licensed.
- CC Licensors with works in Openverse - It is critical that we respect their
  intentions and properly communicate the usage conditions for different license
  attributes (NC, ND, SA, and so on) in our Dataset documentation. We also need
  to spread awareness of the opt-in/out mechanism
  [Spawning AI](https://spawning.ai/) which is integrated with HuggingFace.
- HuggingFace - A key partner responsible for the initial dataset upload,
  providing advice, and potential marketing collaboration
- Creative Commons - Stewards of the Commons and CC Licenses, advisors, and
  another partner in marketing promotion
- Aaron Gokaslan & MosaicML - A researcher working on supplementary datasets and
  providing technical advice

## Infrastructure

<!-- What infrastructural considerations need to be made for this project? If there are none, say so explicitly rather than deleting the section. -->

This project will likely require provisioning some new resources in AWS:

- A dedicated bucket, perhaps a "Requester pays" bucket, for storing the backups
- New scripts to generate backup artifacts

## Accessibility

<!-- Are there specific accessibility concerns relevant to this project? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

This project doesn't directly raise any accessibility concerns. However, we
should be mindful of any changes we would like to make on Openverse.org relating
to copy edits about this initiative.

We should also be mindful of any accessibility issues with HuggingFace's user
interface, which we could share with them in an advisory capacity.

## Marketing

<!-- Are there potential marketing opportunities that we'd need to coordinate with the community to accomplish? If there are none, say so explicitly rather than deleting the section. -->

This release will be a big achievement and we should do quite a bit to promote
it:

- Reach out to past requesters of the dataset and share the HuggingFace link
- Social channel cross-promotion between the WordPress Marketing team,
  HuggingFace, and/or Creative Commons
- Post to more tech-minded communities like HackerNews, certain Reddit
  communities, etc.

Additionally, our documentation will need to be updated extensively to inform
users about the Dataset. The API docs, our developer handbook, our docs site,
and potentially Openverse.org should all be update to reflect these changes.

## Required implementation plans

<!-- What are the required implementation plans? Consider if they should be split per level of the stack or per feature. -->

- Initial Data Dump Creation - A plan describing how to produce and provide
  access to the raw data dumps which will be used to create the Dataset(s).
  Additionally, this plan should address the marketing and documentation of the
  initial data dump. Essentially, all facets of the project relating to the
  initial release.
  - This is the first, largest, and most important plan.
- Dataset Maintenance - A plan describing how we will regularly release updates
  to the Dataset(s).

We will also want a plan for how we intend to _use_ the HuggingFace platform to
complete our other projects for the year, but that might fall outside the scope
of this project.

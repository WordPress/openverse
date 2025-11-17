# 2024-05-30 Implementation Plan: Augment the catalog database with suitable Rekognition tags

**Author**: @AetherUnbound

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @sarayourfriend
- [x] @stacimc

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/431)
- [Project Proposal](/projects/proposals/rekognition_data/20240320-project_proposal_rekognition_data.md)

[aws_rekognition_labels]:
  https://docs.aws.amazon.com/rekognition/latest/dg/samples/AmazonRekognitionLabels_v3.0.zip
[batched_update]: /catalog/reference/DAGs.md#batched-update-dag
[smart_open]: https://github.com/piskvorky/smart_open
[json_lines]: https://jsonlines.org/
[tag_filtering]:
  https://github.com/WordPress/openverse/blob/3747f9aa40ed03899becb98ecae2abf926c8875f/ingestion_server/ingestion_server/cleanup.py#L119-L150

[^batch_tag_example]:
    This issue provides an example of how to manipulate the tags object within
    the [batched update][batched_update] framework:
    https://github.com/WordPress/openverse/issues/1566#issuecomment-2038338095

[^rekognition_data]:
    `s3://migrated-cccatalog-archives/kafka/image_analysis_labels-2020-12-17.txt`

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

```{note}
References throughout this document to "the database" refer exclusively
to the catalog database. The API database is named explicitly where referenced.
```

```{note}
The terms "tags" and "labels" are often used interchangeably in this document. Broadly,
"labels" refer to the actual name of the tag used, and "tags" refer to the blob of
data available in the catalog database which include those labels.
```

This implementation plan describes the technical process we intend to use for
incorporating Rekognition data in the catalog database, and the criteria we will
use when filtering tags as they make their way into the API database. This
includes defining criteria for the following:

- Which tags should be included/excluded in the API
- What minimum accuracy value is required for inclusion

Since there already exist machine-generated tags which may not conform to the
above criteria, a plan is provided for handling those existing tags as well.

```{note}
This document operates under the understanding that the catalog database is Openverse's
data warehouse and should store as much as possible. It's the responsibility of the data
refresh process to dictate what data should be _surfaced_ in the API, and filter where
necessary (see #4541 and #4524 for more details).
```

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

At the end of the implementation of this project, we should have the following:

- Clear criteria for the kinds of tags we will filter when presenting
  machine-generated tags in the API
- A clear minimum accuracy value for machine generated tags
- All available Rekognition tags will be added to the catalog
- An approach for filtering the new Rekognition tags based on the above criteria
- An approach for filtering the existing Clarifai tags until further analysis
  can be performed on the kinds of tags it provides

## Label criteria

This section describes the criteria used for determining which machine-generated
tags we should exclude when adding any new tags to the database, and what the
minimum accuracy cutoff for those tags should be.

### Label selection

<!-- Citations -->

[^1]:
    [N. Garcia, Y. Hirota, Y. Wu and Y. Nakashima, "Uncurated Image-Text Datasets: Shedding Light on Demographic Bias," _2023 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)_, Vancouver, BC, Canada, 2023, pp. 6957-6966, doi: 10.1109/CVPR52729.2023.00672.](https://ieeexplore.ieee.org/document/10204859)

[^2]:
    [Schwemmer C, Knight C, Bello-Pardo ED, Oklobdzija S, Schoonvelde M, Lockhart JW. Diagnosing Gender Bias in Image Recognition Systems. Socius. 2020 Jan-Dec;6:10.1177/2378023120967171. doi: 10.1177/2378023120967171. Epub 2020 Nov 11. PMID: 35936509; PMCID: PMC9351609.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9351609/)

[^3]:
    [D. Zhao, A. Wang, and O. Russakovsky, "Understanding and evaluating racial biases in image captioning," _2021 IEEE/CVF International Conference on Computer Vision (ICCV)_, Oct. 2021, doi: 10.1109/iccv48922.2021.01456.](https://openaccess.thecvf.com/content/ICCV2021/papers/Zhao_Understanding_and_Evaluating_Racial_Biases_in_Image_Captioning_ICCV_2021_paper)

[^4]:
    [I. D. Raji and J. Buolamwini, “Actionable Auditing,” _MIT Media Lab_, Jan. 2019, doi: 10.1145/3306618.3314244.](https://www.aies-conference.com/2019/wp-content/uploads/2019/01/AIES-19_paper_223.pdf)

[^5]:
    [Bass, D. (2019, April 3). Amazon Schooled on AI Facial Technology By Turing Award Winner. _Bloomberg_.](https://www.bloomberg.com/news/articles/2019-04-03/amazon-schooled-on-ai-facial-technology-by-turing-award-winner)

[^6]:
    [Buolamwini, J. (2019, January 25). Response: Racial and Gender bias in Amazon Rekognition — Commercial AI System for Analyzing Faces. _Medium_.](https://medium.com/@Joy.Buolamwini/response-racial-and-gender-bias-in-amazon-rekognition-commercial-ai-system-for-analyzing-faces-a289222eeced)

Machine-generated tags that are the product of AI image labeling models have
been shown repeatedly and consistently to perpetuate certain cultural,
structural, and institutional biases[^1][^2][^3]. This includes analysis done on
[AWS Rekognition](https://docs.aws.amazon.com/rekognition/),
specifically[^4][^5][^6].

Certain demographic axes seem the most likely to result in an incorrect or
insensitive label (e.g. gender assumption of an individual in a photo). For the
reasons described in the above cited works, we should **exclude** labels that
have a demographic context in the following categories:

- Age
- Gender
- Sexual orientation
- Nationality
- Race
- Marital status

There are other categories which might be useful for search relevancy and are
less likely to be applied in an insensitive manner. These labels **should not**
be excluded, unless they are otherwise gendered (e.g. "stewardess", "actress",
etc.). Some examples include:

- Occupation
- Health and disability status
- Political affiliation or preference
- Religious affiliation or preference

### Accuracy selection

[^removal]:
    Note that this step will be moved to a separate filtering step as part of
    #4541

We already filter out existing tags from the catalog when copying data into the
API database during the data refresh's [cleanup step][tag_filtering][^removal].
The minimum accuracy value used for this step is
[0.9 (or 90%)](https://github.com/WordPress/openverse/blob/3747f9aa40ed03899becb98ecae2abf926c8875f/ingestion_server/ingestion_server/cleanup.py#L57-L56)
. AWS's own advice on what value to use is that
[it depends entirely on the use case of the application](https://aws.amazon.com/rekognition/faqs/#Label_Detection).

I took a small sample of the labels we have available (~100MB out of the 196GB
dataset, about 45k images with labels) and performed some exploratory analysis
on the data. I found the following pieces of information:

- **Total images**: 45,059
- **Total labels**: 555,718
- **Average confidence across all labels**: 79.927835
- **Median confidence across all labels**: 81.379463
- **Average confidence per image**: 81.073921
- **Median confidence per image**: 82.564148
- **Number of labels with confidence higher than 90**: 210,341
- **Percentage of labels with confidence higher than 90**: 37.85031%
- **Average number of labels per image higher than 90**: 4.6629

_For a full explanation on this exploration, see:
[Analysis explanation](#analysis-explanation)_

Based on the number of labels we would still be receiving with a confidence
higher than 90, and that 0.9 is already our existing minimum standard, **we
should retain 0.9 or 90% as our minimum label accuracy value** for inclusion in
the API.

This necessarily means that we will not be surfacing a projected 62% of the
labels which are available in the Rekognition dataset. Accuracy, as it directly
relates to search relevancy, is more desirable here than completeness. We will
retain all Rekognition tags in the catalog regardless, and so if we decide to
allow a lower accuracy threshold, we can always adjust the threshold value and
run a new data refresh to surface those tags.

## Step-by-step plan

<!--
List the ordered steps of the plan in the form of imperative-tone issue titles.
The goal of this section is to give a high-level view of the order of implementation any relationships like
blockages or other dependencies that exist between steps of the plan. Link each step to the step description
in the following section.

If special deployments are required between steps, explicitly note them here. Additionally, highlight key
milestones like when a feature flag could be made available in a particular environment.
-->

In order to incorporate accomplish the goals of this plan, the following steps
will need to be performed:

1. [Determine which labels to exclude from Rekognition's label set](#determine-excluded-labels)
2. [Preemptively filter the Rekognition tags](#preemptively-filter-rekognition-tags)
3. [Generate and insert the new Rekognition tags](#insert-new-rekognition-tags)
4. [Filter and assess the existing Clarifai tags](#filter-clarifai-tags)

## Step details

<!--
Describe all of the implementation steps listed in the "step-by-step plan" in detail.

For each step description, ensure the heading includes an obvious reference to the step as described in the
"step-by-step plan" section above.
-->

```{note}
Some of the steps listed below have some cross-over with functionality defined
in/required by the
[data normalization project](/projects/proposals/data_normalization/20240227-implementation_plan_catalog_data_cleaning.md)
(#430) and the
[ingestion server removal project](/projects/proposals/ingestion_server_removal/20240328-implementation_plan_ingestion_server_removal.md)
(#3925). Where possible, existing issues will be referenced and possible duplicated
effort will be identified.
```

### Determine excluded labels

This will involve a manual process of looking through each of the [available
labels for Rekognition][aws_rekognition_labels] and seeing if they match any of
the criteria to be filtered. This process should be completed by two
maintainers, and their list of exclusions discussed & combined. The excluded
labels should then be saved in an accessible location, either on S3 or within
the
[sensitive terms repository](https://github.com/WordPress/openverse-sensitive-terms)
as a new file. Consent & approval should be sought from two other maintainers on
the accuracy of the exclusion list prior to publishing.

### Preemptively filter Rekognition tags

Before inserting the Rekognition tags, we want to make sure they are
appropriately filtered during the data refresh. This filtering can either be the
more complete set of exclusions described above for both the labels themselves
and their accuracy. This, however, depends on the completion of #4541 and the
ingestion server removal project in general (#3925).

In order to work on this effort in parallel with #3925, we can add a check to
the [existing tag filtering step][tag_filtering] which will exclude _all_ tags
with the provider `rekognition`. That way we can add all of the tags to the
catalog with impunity, and allow those tags to be exposed when #3925 is finished
and turned on.

### Insert new Rekognition tags

The below steps describe a thorough, testable, and reproducible way to generate
and incorporate the new Rekognition tags. It would be possible to short-cut many
of these steps by running them as one-off commands or scripts locally (see
[Alternatives](#alternatives)). Since we may need to incorporate machine-labels
in bulk in a similar manner in the future, having a clear and repeatable process
for doing so will make those operations easier down the line. It also allows us
to test the insertion process locally, which feels crucial for such a
significant addition of data.

#### Context

The Rekognition dataset we have available is a [JSON lines][json_lines] file
where each line is a JSON object with (roughly) the following shape:

```json
{
  "image_uuid": "960b59e6-63f7-4beb-9cd0-6e3a275991a8",
  "response": {
    "Labels": [
      {
        "Name": "Human",
        "Confidence": 99.82632446289062,
        "Instances": [],
        "Parents": []
      },
      {
        "Name": "Person",
        "Confidence": 99.82632446289062,
        "Instances": [
          {
            "BoundingBox": {
              "Width": 0.219997838139534,
              "Height": 0.46728312969207764,
              "Left": 0.6179072856903076,
              "Top": 0.39997851848602295
            },
            "Confidence": 99.82632446289062
          },
          ...
        ],
        "Parents": []
      },
      {
        "Name": "Crowd",
        "Confidence": 93.41161346435547,
        "Instances": [],
        "Parents": [
          {
            "Name": "Person"
          }
        ]
      },
      {
        "Name": "People",
        "Confidence": 86.95382690429688,
        "Instances": [],
        "Parents": [
          {
            "Name": "Person"
          }
        ]
      },
      {
        "Name": "Game",
        "Confidence": 68.61305236816406,
        "Instances": [],
        "Parents": [
          {
            "Name": "Person"
          }
        ]
      },
      {
        "Name": "Chess",
        "Confidence": 68.61305236816406,
        "Instances": [
          {
            "BoundingBox": {
              "Width": 0.8339029550552368,
              "Height": 0.7898563742637634,
              "Left": 0.08363451808691025,
              "Top": 0.1719469130039215
            },
            "Confidence": 68.61305236816406
          }
        ],
        "Parents": [
          {
            "Name": "Game"
          },
          {
            "Name": "Person"
          }
        ]
      },
      {
        "Name": "Coat",
        "Confidence": 68.09342193603516,
        "Instances": [],
        "Parents": [
          {
            "Name": "Clothing"
          }
        ]
      },
      {
        "Name": "Suit",
        "Confidence": 68.09342193603516,
        "Instances": [],
        "Parents": [
          {
            "Name": "Overcoat"
          },
          {
            "Name": "Coat"
          },
          {
            "Name": "Clothing"
          }
        ]
      },
      {
        "Name": "Apparel",
        "Confidence": 68.09342193603516,
        "Instances": [],
        "Parents": []
      },
      {
        "Name": "Clothing",
        "Confidence": 68.09342193603516,
        "Instances": [],
        "Parents": []
      },
      {
        "Name": "Overcoat",
        "Confidence": 68.09342193603516,
        "Instances": [],
        "Parents": [
          {
            "Name": "Coat"
          },
          {
            "Name": "Clothing"
          }
        ]
      },
      {
        "Name": "Meal",
        "Confidence": 62.59776306152344,
        "Instances": [],
        "Parents": [
          {
            "Name": "Food"
          }
        ]
      },
      {
        "Name": "Food",
        "Confidence": 62.59776306152344,
        "Instances": [],
        "Parents": []
      },
      {
        "Name": "Furniture",
        "Confidence": 58.1875,
        "Instances": [],
        "Parents": []
      },
      {
        "Name": "Tablecloth",
        "Confidence": 57.604129791259766,
        "Instances": [],
        "Parents": []
      },
      {
        "Name": "Party",
        "Confidence": 57.07652282714844,
        "Instances": [],
        "Parents": []
      },
      {
        "Name": "Dinner",
        "Confidence": 56.07081985473633,
        "Instances": [],
        "Parents": [
          {
            "Name": "Food"
          }
        ]
      },
      {
        "Name": "Supper",
        "Confidence": 56.07081985473633,
        "Instances": [],
        "Parents": [
          {
            "Name": "Food"
          }
        ]
      }
    ],
    "LabelModelVersion": "2.0",
    "ResponseMetadata": {
      "RequestId": "60c4b6f5-3b73-466e-8fa5-e40037661253",
      "HTTPStatusCode": 200,
      "HTTPHeaders": {
        "content-type": "application/x-amz-json-1.1",
        "date": "Thu, 29 Oct 2020 19:46:02 GMT",
        "x-amzn-requestid": "60c4b6f5-3b73-466e-8fa5-e40037661253",
        "content-length": "3526",
        "connection": "keep-alive"
      },
      "RetryAttempts": 0
    }
  }
}
```

This file is about 200GB in total. For more information about the data, see
[Analysis Explanation](#analysis-explanation).

#### DAG

```{attention}
A snapshot of the catalog database should be created prior to running this step
in production.
```

We will create a DAG (`add_rekognition_labels`) which will perform the following
steps:

1. Create a temporary table in the catalog for storing the tag data. This table
   will be two columns: `identifier` and `tags` (with data types matching the
   existing catalog columns).
2. Iterate over the large Rekognition dataset in a chunked manner using
   [`smart_open`][smart_open]. `smart_open` provides
   [options for tuning buffer size](https://github.com/piskvorky/smart_open?tab=readme-ov-file#transport-specific-options)
   so larger chunks can be read into memory.
   1. For each line, read in the JSON object and pull out the top-level labels &
      confidence values. **Note**: some records may not have any labels.
   2. Construct a `tags` JSON object similar to the existing tags data for that
      image, including accuracy and provider. Ensure that the labels are lower
      case and that the confidence value is between 0.0 and 1.0 (e.g.
      `[{"name": "cat", "accuracy": 0.9983, "provider": "rekognition"}, ...]`).
   3. At regular intervals, insert batches of constructed `identifier`/`tags`
      pairs into the temporary table.
3. Launch a [batched update run][batched_update] which merges the existing tags
   and the new tags from the temporary table for each
   identifier[^batch_tag_example]. **Note**: the batched update DAG may need to
   be augmented in order to reference data from an existing table, similar to
   #3415.
4. Delete the temporary table.

For local testing, a small sample of the Rekognition data could be made
available in the local S3 server
[similar to the iNaturalist sample data](https://github.com/WordPress/openverse/blob/82282a00abdaed21e8381052a874d8ab9a4f7e0a/catalog/compose.yml#L98-L101).

### Filter Clarifai tags

While this project seeks to add new magine-generated labels to the database, we
already have
[around 10 million records](https://github.com/WordPress/openverse/pull/3948#discussion_r1552301581)
which include labels from the
[Clarifai image labeling service](https://www.clarifai.com/products/scribe-data-labeling-platform).
It is unclear how these labels were applied, or what the exhaustive label set
is. Thus, it's prudent for us to perform some analysis on these tags to
determine which labels from this dataset should also be filtered from the API.

```{note}
We will **not** be removing any existing tags from the catalog.
```

Similar to the
[preemptive Rekognition filtering](#preemptively-filter-rekognition-tags), we
will want to filter the existing Clarifai tags until we can perform the same
analysis on the set of available tags
[as will be done for the Rekognition ones](#determine-excluded-labels). This can
be done using the same steps described for the Rekognition filtering, based on
the status of this project and #3925.

Once the filtering is in place, we can construct an exhaustive set of Clarifai
labels and determine exclusions for that provider using the approach
[described above](#label-criteria). Then the Clarifai label exclusions can be
added to #4541 in the same way Rekognition's are added and the blanked exclusion
for all tags from that provider can be lifted. These exclusion lists could be
combined into a single filtering step, or we could have individual filter lists
based on the label provider. My preference is former, since that way the single
list serves as a more exhaustive exclusion list.

## Dependencies

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

No infrastructure changes will be necessary for this work.

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

The [`smart_open` package][smart_open] will need to be installed as a dependency
within Airflow, in order for it to be available for this DAG.

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

This project intersects with the ingestion server removal project (#3925), but
steps can be taken to circumvent this dependency for the time being. See
[preemptively filter Rekognition tags](#preemptively-filter-rekognition-tags)
for more details.

This project is also related to, but not necessarily dependent on, the data
normalization project. See the note in [Step Details](#step-details).

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

Although the above plan is thorough and may require more investment up-front, we
could opt to incorporate this data as soon as possible by performing all of the
[steps of the DAG](#dag) by hand. We would need to record what exact set of
steps were taken, as there would likely be some iteration on scripts and SQL as
part of figuring out the exact commands necessary. The entire Rekognition
file[^rekognition_data] could be downloaded by a maintainer locally and all data
manipulation could be performed on their machine. A new TSV could be generated
matching the table pattern described in [DAG step 1](#dag), the file could be
uploaded to S3, and a table in Postgres could be created from it directly. The
final batched update step would then be kicked off by hand.

While I would personally prefer to take these actions by hand to get the data in
quicker, I think it's prudent for us to have a more formal process for
accomplishing this. It's possible that we might receive more machine-generated
labels down the line, and having a rubric for how to add them will serve us much
better than a handful of scripts and instructions.

We could also skip processing the Rekognition file in Python and insert it
directly into Postgres. We'd then need to perform the label extraction and
filtering from the JSON objects using SQL instead, which
[does seem possible](https://stackoverflow.com/a/33130304). This would obviate
the need to use `smart_open` and install a new package on Airflow. I think this
route will be much harder based on my own experience crafting queries involving
Postgres's JSON access/manipulation methods, and I think the resulting query
would not be as much of a benefit as the time it might take to craft it.

## Blockers

<!-- What hard blockers exist that prevent further work on this project? -->

No blockers, this work can begin immediately (though some may conflict with the
data normalization and ingestion server removal projects, see the note in
[dependencies](#other-projects-or-work)).

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

Rollback for this project looks different for each label source:

- [**Clarifai**](#filter-clarifai-tags): If we decide to roll back any filters
  for Clarifai that we instated, we could simply remove those filters and
  re-surface the data in the API. We're not removing any data from the catalog
  as part of this project, so this would return the Clarifai tags to their
  currently fully-visible state.
- [**Rekognition**](#insert-new-rekognition-tags): If we decide not to surface
  _any_ Rekognition tags in the API, we could simply retain the
  [blanket provider-wide filter for all Rekognition tags](#preemptively-filter-rekognition-tags).

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

We are only adding new data to the catalog as part of this effort; we do not
intend to remove any existing data. We have full control over what data we
filter when constructing the API database during the data refresh, and so we
could opt to filter out all of the machine-generated labels that exist in the
database even after the new ones are inserted. As such, this project poses
little risk beyond increased database storage size.

Adding this new data will affect search relevancy. Discussion around that risk
can be found
[in the project proposal](20240320-project_proposal_rekognition_data.md#success).

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

Previous examples for tag manipulation using the batched update DAG are shared
throughout[^batch_tag_example].

## Analysis explanation

I downloaded the first 100MB of the file using the following command:

```bash
aws s3api get-object --bucket migrated-cccatalog-archives --key kafka/image_analysis_labels-2020-12-17.txt --range bytes=0-100000000 ~/misc/aws_rekognition_subset.txt
```

The S3 file referenced here is a [JSON lines][json_lines] file where each line
is a record for an image. I had to delete the last line because a byte selection
couldn't guarantee that the entire line would be read in completely, and it
might not parse as valid JSON.

Then I used [`pandas`](https://pandas.pydata.org/) and ipython for further
exploration. Below is the script I used to ingest the data and compute the
values referenced in [the accuracy selection section](#accuracy-selection):

```python
import json
import pandas as pd

# Read the file in as JSON lines
df = pd.read_json("/home/madison/misc/aws_rekognition_subset.txt", lines=True)

# Extract the labels from each row into mini-dataframes
recs = []
for _, row in df.iterrows():
  iid = row.image_uuid
  try:
    # Normalize the labels into a table, then get only the name and confidence values
    # Skip the record if it doesn't have labels
    tags = pd.json_normalize(row.response["Labels"])[["Name", "Confidence"]]
  except KeyError:
    continue
  # Add the image ID as an index
  tags["image_uuid"] = iid
  recs.append(tags)

# Concatenate all dataframes together
# This results in the columns: image_uuid, name, confidence
xdf = pd.concat(recs)

# Compute the total number of labels
len(xdf)

# Get average statistics for the dataframe, namely confidence mean
xdf.describe()

# Average confidence by image
xdf.groupby("image_uuid").mean("Confidence").mean()

# Global median confidence
xdf.Confidence.median()

# Median confidence by image
xdf.groupby("image_uuid").median("Confidence").median()

# Number of labels w/ confidence higher than 90
(xdf.Confidence > 90).sum()

# Percent of total labels w/ confidence higher than 90
(xdf.Confidence > 90).sum() / len(xdf)

# Average number of tags per item w/ confidence higher than 90
(xdf.Confidence > 90).sum() / len(df)
```

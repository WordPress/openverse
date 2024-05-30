# 2024-05-30 Implementation Plan: Augment the catalog database with suitable Rekognition tags

**Author**: @AetherUnbound

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @obulat
- [ ] @stacimc

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/431)
- [Project Proposal](/projects/proposals/rekognition_data/20240320-project_proposal_rekognition_data.md)

[aws_rekognition_labels]:
  https://docs.aws.amazon.com/rekognition/latest/dg/samples/AmazonRekognitionLabels_v3.0.zip

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

**NB**: References throughout this document to "the database" refer exclusively
to the catalog database.

This implementation plan describes the criteria with which we will select which
tags from the Rekognition data to include into the catalog database. This
includes defining criteria for the following:

- Which tags should be included/excluded
- What minimum accuracy value is required for inclusion

It also describes the technical process which will be necessary for performing
the insertion of the Rekognition tags. Since there already exist
machine-generated tags which may not conform to the above criteria, a plan is
provided for removing those existing tags as well.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

At the end of the implementation of this project, we should have the following:

- Clear criteria for the kinds of tags we will exclude when inserting
  machine-generated tags
- A clear minimum accuracy value for machine generated tags
- Existing Clarifai tags which do not match the above criteria will be removed
  from the database
- New Rekognition tags which do match the above criteria will be added to the
  database

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

[^4]:
    [Bass, D. (2019, April 3). Amazon Schooled on AI Facial Technology By Turing Award Winner. _Bloomberg_.](https://www.bloomberg.com/news/articles/2019-04-03/amazon-schooled-on-ai-facial-technology-by-turing-award-winner)

[^5]:
    [Buolamwini, J. (2019, January 25). Response: Racial and Gender bias in Amazon Rekognition — Commercial AI System for Analyzing Faces. _Medium_.](https://medium.com/@Joy.Buolamwini/response-racial-and-gender-bias-in-amazon-rekognition-commercial-ai-system-for-analyzing-faces-a289222eeced)

Machine-generated tags that are the product of AI image labeling models have
been shown repeatedly and consistently to perpetuate certain cultural,
structural, and institutional biases[^1][^2][^3]. This includes analysis done on
[AWS Rekognition](https://docs.aws.amazon.com/rekognition/),
specifically[^4][^5][^6].

For the reasons described in the above cited works, we should exclude labels
that have a demographic context in the following categories:

- Age
- Gender
- Sexual orientation
- Nationality
- Race

These seem the most likely to result in an incorrect or insensitive label (e.g.
gender assumption of an individual in a photo). There are other categories which
might be useful for search relevancy and are less likely to be applied in an
insensitive manner. Some examples include:

- Occupation
- Marital status
- Health and disability status
- Political affiliation or preference
- Religious affiliation or preference

### Accuracy selection

[removal]: Note that this step will be going away as part of #430

We already filter out existing tags from the catalog when copying data into the
API database during the data refresh's
[cleanup step](https://github.com/WordPress/openverse/blob/3747f9aa40ed03899becb98ecae2abf926c8875f/ingestion_server/ingestion_server/cleanup.py#L119-L150)[^removal].
The minimum accuracy value used for this step is
[0.9](https://github.com/WordPress/openverse/blob/3747f9aa40ed03899becb98ecae2abf926c8875f/ingestion_server/ingestion_server/cleanup.py#L57-L56),
or 90%. AWS's own advice on what value to use is essentially that
[it depends on the use case of the application](https://aws.amazon.com/rekognition/faqs/#Label_Detection).

I took a small sample of the labels we have available (~100MB out of the 196GB
dataset, about 45k images with labels) and performed some exploratory analysis
on the data. I found the following pieces of information:

- **Total images**: 45,059
- **Total labels**: 555,718
- **Average confidence across all labels**: 79.927835
- **Median confidence across all labels**: 81.379463
- **Average confidence per image**: 81.073921
- **Median confidence per image**: 82.564148
- **Number of labels with confidence higher than 90**: 210341
- **Percentage of labels with confidence higher than 90**: 37.85031%
- **Average number of labels per image higher than 90**: 4.6629

Based on the number of labels we would still be receiving with a confidence
higher than 90, and that 90 is already our existing minimum standard, we should
retain 0.9 or 90% as our minimum label accuracy value for inclusion in the
catalog.

This necessarily means that we will not be including a projected 62% of the
labels which are available in the Rekognition dataset. Accuracy, as it directly
relates to search relevancy, is more desirable here than completeness. We will
retain the original Rekognition source data after ingesting the high-accuracy
tags, and so if we decide to allow a lower accuracy threshold, we can always
re-add the lower confidence values.

(Note: need to consider clarifai deletions, which would happen anyway with the
data normalization)

## Step-by-step plan

<!--
List the ordered steps of the plan in the form of imperative-tone issue titles.
The goal of this section is to give a high-level view of the order of implementation any relationships like
blockages or other dependencies that exist between steps of the plan. Link each step to the step description
in the following section.

If special deployments are required between steps, explicitly note them here. Additionally, highlight key
milestones like when a feature flag could be made available in a particular environment.
-->

## Step details

<!--
Describe all of the implementation steps listed in the "step-by-step plan" in detail.

For each step description, ensure the heading includes an obvious reference to the step as described in the
"step-by-step plan" section above.
-->

## Dependencies

### Feature flags

<!-- List feature flags/environment variables that will be utilised in the development of this plan. -->

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

## Design

<!-- Note any design requirements for this plan. -->

## Blockers

<!-- What hard blockers exist that prevent further work on this project? -->

## API version changes

<!-- Explore or mention any changes to the API versioning scheme. -->

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

## Privacy

<!-- How does this approach protect users' privacy? -->

## Localization

<!-- Any translation or regional requirements? Any differing legal requirements based on user location? -->

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

## Analysis explanation

I downloaded the first 100MB of the file using the following command:

```bash
aws s3api get-object --bucket migrated-cccatalog-archives --key kafka/image_analysis_labels-2020-12-17.txt --range bytes=0-100000000 ~/misc/aws_rekognition_subset.txt
```

The S3 file referenced here is a [JSON lines](https://jsonlines.org/) file where
each line is a record for an image. I had to delete the last line because a byte
selection couldn't guarantee that the entire line would be read in completely,
and it might not parse as valid JSON.

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

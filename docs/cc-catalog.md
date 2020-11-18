<!-- TITLE: CC Catalog -->
<!-- SUBTITLE: Information about the CC Catalog -->

# About
**CC Catalog** is our database of metadata about CC-licensed works from across
the internet. This data is found and parsed via Common Crawl data and open APIs
and the code is located in the
[cccatalog](https://github.com/creativecommons/cccatalog) repository.

The CC Catalog powers the CC Catalog API and CC Search. For more details, see
the main [CC Search](/tech/cc-search) page.

# Data Table
The main data of the CC Catalog is in the PostgreSQL table `image` (in the
`openledger` database). The schema of the table (annotated with source) is:

|         Column          |           Type            |    Comes From |
| ----------------------- | ------------------------- | ------------------------------ |
| id                      | integer                   | DB-generated |
| created_on              | timestamp with time zone  | script-generated (now) |
| updated_on              | timestamp with time zone  | script-generated (now) |
| identifier              | uuid                      | DB-generated |
| perceptual_hash         | character varying(255)    | Not Used |
| provider                | character varying(80)     | script-generated |
| source                  | character varying(80)     | script-generated  |
| foreign_identifier      | character varying(3000)   | metadata |
| foreign_landing_url     | character varying(1000)   | metadata |
| url                     | character varying(3000)   | metadata |
| thumbnail               | character varying(3000)   | metadata |
| width                   | integer                   | metadata |
| height                  | integer                   | metadata |
| filesize                | integer                   | No longer used (appears to be null for new entries) |
| license                 | character varying(50)     | metadata |
| license_version         | character varying(25)     | metadata |
| creator                 | character varying(2000)   | metadata |
| creator_url             | character varying(2000)   | metadata |
| title                   | character varying(5000)   | metadata |
| tags_list               | character varying(255)[]  | unused (always null) |
| last_synced_with_source | timestamp with time zone  | script-generated (now) |
| removed_from_source     | boolean                   | script-generated (f) |
| meta_data               | jsonb                     | metadata |
| tags                    | jsonb                     | metadata |
| watermarked             | boolean                   | script-generated |
| view_count              | integer                   | unused (initialized to 0) |


# Providers
Providers are sites that host CC-licensed works. We have direct partnerships
with some of our providers and ingest their content through their public APIs.
However, we identify new providers mainly through processing [Common
Crawl](https://commoncrawl.org/) data. Potential providers are reviewed
according to the [CC Search Provider Review Process][cc_search_review].

[cc_search_review]: https://docs.google.com/document/d/18WE7rKRAIXpTSTJh4RUSc50tSi4KrOP6lIjxrCj-kb8/edit#heading=h.nyxpan77y2x6


The current providers are
* [Flickr](/tech/cc-search/cc-catalog/flickr)
* [Wikimedia Commons](/tech/cc-search/cc-catalog/wikimediacommons)
* [Thingiverse](/tech/cc-search/cc-catalog/thingiverse)
* [Met Museum](/tech/cc-search/cc-catalog/metmuseum)
* [PhyloPic](/tech/cc-search/cc-catalog/phylopic)
* [Cleveland Museum of Art](/tech/cc-search/cc-catalog/clevelandmuseumofart)
* [RawPixel](/tech/cc-search/cc-catalog/rawpixel)

Providers to review are tracked via Github issues, see the **Resources** section
for a list of issues.

# Resources

* [Common Crawl Providers Review](https://docs.google.com/spreadsheets/d/1Mm-MIgjDkqFIZe1jFLOBRbIhtguueZINRlc3FH2dykY/) spreadsheet
* [Provider identification GitHub tickets](https://github.com/creativecommons/cccatalog/issues?utf8=%E2%9C%93&q=label%3Aproviders+)
* [Legal and reputational risk management](https://docs.google.com/document/d/1r5BzWiQkmXePi9m0cX-FLyAgh47Fny8DZTOtdkRTLbM/edit)
* [CC Catalog Documentation](https://docs.google.com/document/d/1HVrfQRgW3zZ9X7A7k8nbOwR-9liysjPK6MabsOxnPB8/edit)


# Data Process Flow & Management

The purpose of CC Catalog is to facilitate the discovery of 1.4 billion CC
licensed content by leveraging open data from Common Crawl and open APIs.

## Airflow - Workflow Management

Apache Airflow is used to manage the workflow for the various API ETL jobs and
will sync the extracted Common Crawl image data to the upstream database. Here
is the [GitHub issue](https://github.com/creativecommons/cccatalog/issues/177)
with links to the various issues, jobs and source code.

The workflows can be been managed from the [Admin Panel][airflow_dashboard].

[airflow_dashboard]: http://airflow.creativecommons.engineering/admin/

### Production deployment

To deploy new Airflow DAGs or Provider API Scripts to production, follow these
steps:

1. `ssh ec2-user@ec2-54-85-128-241.compute-1.amazonaws.com` (ask Alden or Brent to add your keys if necessary)
2. `cd cccatalog/src/cc_catalog_airflow`
3. If necessary, copy environment data from Lastpass to `.env` in this directory.
4. `git fetch --all`
5. `git checkout tags/<TAG_ID>`
6. `./deploy_in_prod.sh`
7. (optional) Navigate to the [Admin Panel][airflow_dashboard] to see things working (or failing to work, as the case may be).

**Note:**  If you do this while a particular job is running, that job will fail.  But, the context will be saved, so the job should be retried once the new container comes up.

### Weekly airflow log rotation

At the moment, the airflow scheduler logs **absolutely must** be rotated weekly
in order to avoid filling up the disk (thereby breaking everything that runs on
the host ec2 instance, even potentially the docker daemon). For instructions see
[this page](/tech/cc-search/cc-catalog/airflowrotation)

## AWS Managed Services
* **[Common Crawl Data Pipelines](https://console.aws.amazon.com/datapipeline/home?region=us-east-1)**
    The [Common Crawl](http://commoncrawl.org/) corpus containes petabytes of [web crawl data](http://commoncrawl.org/the-data/get-started/). Common Crawl publishes a new dataset at the end of each month. An EMR cluster of 100 c4.8xlarge is configured to automatically parse the data to identify all domains that link to creativecommons.org. Spot pricing is used to keep the cost of this job under $100 and the number of instances keeps the execution time under 1 hour (±10 minutes). If the execution time increases it may be time to scale up (or out). Benchmarking has shown that the **R3/R4** instance family are also suitable for this job, however the spot pricing fluctuates. 
    * Name: Common Crawl ETL - Extract all domains that link to creativecommons.org and save the output in Parquet files.
    Queries can be performed using the data to identify potential providers for inclusion in CC Search. A query has been developed to help with this process and it is saved in Athena 
    * query name: [Top_CC_Licensed_Domains](https://console.aws.amazon.com/athena/home?force&region=us-east-1#query/saved/4e12dfa7-e310-4847-872a-0ebff12db6ad). This query requires the user to specify the common crawl partition that should be analyzed. 
		
    All providers that pass the **Provider Review Process** have been integrated in another data pipeline, which extracts the image URL if it links to a Creative Commons license.
    * Name: Common Crawl Provider Images ETL - Extract image URL and associated meta data, if it links to a CC license.

* **[Glue Job](https://us-east-1.console.aws.amazon.com/glue/home?region=us-east-1#etl:tab=jobs)**
    * Name: ProcessCommonCrawlData
    * Description: Aggregate the most recent common crawl data and move it from the script's working directory to the interim **Data Lake** location. A partition is also created, so that the data can be analyzed by partitions (which helps to minimize costs).

* **[Glue ETL Trigger](https://us-east-1.console.aws.amazon.com/glue/home?region=us-east-1#etl:tab=triggers)**
    * Name: trg_ProcessCommonCrawlData
    * Description: Trigger the execution of the "ProcessCommonCrawlData" job. This runs on the 7th day of each month at 11PM

* **[Glue Crawler](https://us-east-1.console.aws.amazon.com/glue/home?region=us-east-1#catalog:tab=crawlers)**
    * Name: LoadCommonCrawlData
    * Description: This refreshes the commonsmapper database in Athena and will also load recently added data/partitions. This runs on the 7th day of each month at 11:30PM (after the new partition has been moved to the interim **Data Lake**.

* **[Athena](https://console.aws.amazon.com/athena/home?region=us-east-1#query)**
    * This is the UI to query the partitioned common crawl data.


* **S3 buckets**
    * [commonsmapper](https://s3.console.aws.amazon.com/s3/buckets/commonsmapper/?region=us-east-1&tab=overview)
        * licenses_by_domain: **defunct: this was used by the former Director of Product Engineering**
        * common_crawl_image_data: the output directory for cc licensed images that were extracted from each provider. The directory structure is `common_crawl_index/provider_name/filename.csv`
    * [commonsmapper-v2](https://s3.console.aws.amazon.com/s3/buckets/commonsmapper-v2/?region=us-east-1&tab=overview)
        * scripts: contains the files that are used by the EMR cluster.
        * bootstrap: config files for the EMR cluster.
        * output: temporary output location for the Common Crawl Data pipeline => "Common Crawl ETL". I manually cleanup this directory after confirming that all operations were performed successfully by the AWS EMR Cluster & Glue Jobs.
        * log: this will be your best friend to debug any issues.
            * pipeline/df-01792251K0EHZMVMJQ82: log files for the "Common Crawl ETL" data pipeline.
            * pipeline/df-09203082Y9C4462IMYIB: log files for the "Common Crawl Provider Images ETL" data pipeline.
        * data: The interim **Data Lake**. The data is partitioned using its respective [Common Crawl index](https://index.commoncrawl.org/). 

* **AWS Key** 
    * Key pair name is cc-catalog. Saved in the Shared-CC Catalog folder in LastPass, filename => **cc-catalog key**.
 
## Archive 
* [RSync.net](https://www.rsync.net/) is used to store archived common crawl data. Login info is in LastPass.

# Research
Internal AI policy:
> Following internal review and discussion, we have concluded that as an organization and team, we do not wish to engage contractors or services in ways that would facilitate the development of military applications of technology. This includes, but is not limited to, the use of data that is supplied by CC through any means in connection with the services that contributes to the training of artificial intelligence and image recognition tools by the service provider. 
>
> CC staff will make reasonable efforts during procurement and partnership processes to evaluate service providers to determine how our data or contributions will be used including, without limitation, whether it is used in service of such initiatives. This will include evaluating contractual terms of engagement and requesting modifications that preclude such uses when feasible. If after entering an agreement, it is determined that this is the case, CC management will determine the best course of action, which may involve canceling the service or partnership.

(see [Creative Commons Contracting Philosophy and Processes](https://docs.google.com/document/d/1U9b_VNZrCEN9sKH7ZQ7ljFcCi9eJmai3xf_RqghHCEo/) for background information).

* [Potential Image Analysis Providers - Google Sheets](https://docs.google.com/spreadsheets/d/1Lw7j8W_QomcEBvjo-908JCmlPliI9nBAxNzBZ-bh0vA/edit#gid=0) (Potential Image Tagging AI Providers)
* [Open Source Image Tagging Libraries - Google Sheets](https://docs.google.com/spreadsheets/d/1JCFavh0OgIXs0etswWmYKrdmWKy4Pk53qV7OuzSXCPU/edit#gid=0)

## AWS Imagine Grant

We received a grant based on the proposal [here][aws_grant_2019]. As an early
step, we want to determine which images in CC Catalog are the best candidates to
have tags added to them by Amazon Rekognition.  We would therefore like to
determine which photos are the most popular on some of our larger providers.  In
particular, we would like to be able to filter out some images from the
following providers:

* Wikimedia Commons -- Currently, there isn't too much from this provider in the
  DB, but we expect it to grow quickly
* Flickr -- This is the most prolific provider in our DB.  As of 2019-01-22,
  there are 314 million images from Flickr in the `image` table.

The end goal is to reduce the scope to the best 100 million images in our DB for
this analysis.

Currently, we'd like do something along the lines of

1. Take all images from museums and other 'high-quality' providers
2. Take the images from Category:Quality Images from Wikimedia Commons
3. Determine the popularity of other images on Wikimedia Commons using a
   `globalusage` query.  For an example, see the Global Usage of
   [File:Cat poster 1.jpg][cats_image] from Wikimedia Commons
4. Determine the popular images from Flickr, using their 'views' metric, which
   is already available as an 'extra' in the [Request][flickr_request] we
   already use to get images from their API.
   
Steps 3 and 4 above should be used to determine which images from Wikimedia
Commons and Flickr to use for the project. Note that the metrics are not
strictly comparable, so we should decide ahead of time what proportion we want
from each of these sources.

### Regular reingestion of current image information

Currently, we generally only get information about a given image when it is
first uploaded to one of our larger providers.  For popularity data, this won't
suffice; It's not very meaningful to know how many views an image has just after
it was uploaded.  Thus, we have come up with a strategy that will allow us to
update info about images uploaded in the past regularly, with a preference
towards 'freshening' the information about recently uploaded images.  This will
also (in the future) allow us to remove images that were taken down at the
source from CC Search.  The strategy is outlined [here][freshness_strategy].

[aws_grant_2019]: https://drive.google.com/drive/folders/1eXDGbOKnbvfMUcwnLrFg-1I7tCvFfvtN
[cats_image]: https://commons.wikimedia.org/w/api.php?action=query&prop=globalusage&gulimit=max&gunamespace=0&titles=File:Cat_poster_1.jpg
[flickr_request]: https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=YOUR_KEY_HERE&min_upload_date=2020-01-22%2013:00:00&max_upload_date=2020-01-22%2013:05:00&license=1&media=photos&content_type=1&extras=description,license,date_upload,date_taken,owner_name,tags,o_dims,views,url_t,url_s,url_m,url_l&per_page=500&format=json&nojsoncallback=1&page=1
[freshness_strategy]: /tech/cc-search/cc-catalog/image-data-reingestion-strategy

## Long term Image ranking ideas.

In the long run, and in order to have 'fair' metrics that are comparable across
different providers, it may prove fruitful to consider trying to determine,
e.g., how many times a given image is direct-linked on the internet.  These
sorts of metrics would probably be easiest to glean from Common Crawl.

# Community Involvement

We would like to increase the level of community contribution to CC Catalog. Details can be found at the [CC Catalog Community Involvement][ccc_community_involvement] page.

[ccc_community_involvement]: cc-catalog/cc-catalog-community-involvement

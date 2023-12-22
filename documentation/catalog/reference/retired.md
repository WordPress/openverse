# Retired

## Web Crawl Data (retired)

The Common Crawl Foundation provides an open repository of petabyte-scale web
crawl data. A new dataset is published at the end of each month comprising over
200 TiB of uncompressed data.

The data is available in three file formats:

- WARC (Web ARChive): the entire raw data, including HTTP response metadata,
  WARC metadata, etc.
- WET: extracted plaintext from each webpage.
- WAT: extracted html metadata, e.g. HTTP headers and hyperlinks, etc.

For more information about these formats, please see the [Common Crawl
documentation][ccrawl_doc].

Openverse Catalog used AWS Data Pipeline service to automatically create an
Amazon EMR cluster of 100 c4.8xlarge instances that parsed the WAT archives to
identify all domains that link to creativecommons.org. Due to the volume of
data, Apache Spark was also used to streamline the processing. The output of
this methodology was a series of parquet files that contain:

- the domains and its respective content path and query string (i.e. the exact
  webpage that links to creativecommons.org)
- the CC referenced hyperlink (which may indicate a license),
- HTML meta data in JSON format which indicates the number of images on each
  webpage and other domains that they reference,
- the location of the webpage in the WARC file so that the page contents can be
  found.

The steps above were performed in [`ExtractCCLinks.py`][ex_cc_links].

This method was retired in 2021.

[ccrawl_doc]: https://commoncrawl.org/the-data/get-started/
[ex_cc_links]:
  https://github.com/WordPress/openverse/blob/c20262cad8944d324b49176678b16b230bc57e2e/archive/ExtractCCLinks.py

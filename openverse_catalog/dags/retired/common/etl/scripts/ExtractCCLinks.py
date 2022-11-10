# flake8: noqa
# Common Crawl data extraction
"""Identify all links to Creative Commons in the web crawl data"""

import gzip
import logging
import os
import re
import sys
from collections import Counter

import boto3
import botocore
import requests
import StringIO
import ujson as json
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from urlparse import urlparse
from warcio.archiveiterator import ArchiveIterator


BUCKET = os.environ.get("COMMONCRAWL_BUCKET", "not_set")


class CCLinks:
    def __init__(self, _index, _ptn=2500):
        """
        CCLinks constructor: Validate the user-defined index based on Common Crawl's expected format.
        If the pattern is valid, it generates 1) a url for the WAT path and 2) the location to output the results.

        Parameters
        ------------------
        _index: string
            The common crawl index name

        _ptn: integer
            The number of partitions for the spark job

        Returns
        ------------------
        None

        """

        self.crawlIndex = _index

        # check index format
        pattern = re.compile(r"CC-MAIN-\d{4}-\d{2}")
        if not pattern.match(_index):
            logging.error(f"Invalid common crawl index format => {_index}.")
            sys.exit()

        self.numPartitions = _ptn
        self.url = "https://{}.s3.amazonaws.com/crawl-data/{}/wat.paths.gz".format(
            BUCKET, self.crawlIndex
        )
        self.output = f"s3://commonsmapper-v2/output/{self.crawlIndex}"

    def loadWATFile(self):
        # load the WAT file paths
        """
        Make a request for a WAT file using the url, that was defined in the constructor.

        Parameters
        ------------------
        None

        Returns
        ------------------
        list
            A list of WAT path locations.
        """
        logging.info(f"Loading file {self.url}")

        try:
            response = requests.get(self.url)

            if response.status_code == requests.codes.ok:
                content = StringIO.StringIO(response.content)
                fh = gzip.GzipFile(fileobj=content)
                watPaths = fh.read().split()

                return watPaths
            else:
                raise Exception

        except Exception as e:
            logging.error("There was a problem loading the file.")
            logging.error(f"{type(e).__name__}: {e}")
            # sys.exit()

    def processFile(self, _iterator):
        """
         Parse each WAT file to identify domains with a hyperlink to creativecommons.org.

         Parameters
         ------------------
        _iterator: iterator object
             The iterator for the RDD partition that was assigned to the current process.

         Returns
         ------------------
         list
             A list of domains and their respective content path and query string, the hyperlink to creative commons (which may reference a license), the location of the domain in the current warc file and a count of the number of links and images.
        """

        logging.basicConfig(
            format="%(asctime)s: [%(levelname)s - ExtractCCLinks] =======> %(message)s",
            level=logging.INFO,
        )

        # connect to s3 using boto3
        s3 = boto3.resource("s3")
        # s3.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)

        try:
            # verify bucket
            s3.meta.client.head_bucket(Bucket=BUCKET)
        except botocore.exceptions.ClientError as e:
            error = int(e.response["Error"]["Code"])

            if error == 404:
                logging.error("Bucket not found!")
                sys.exit()

        else:
            # iterate over the keys and load the respective wat files
            for uri in _iterator:

                try:
                    # verify key
                    s3.Object(BUCKET, uri.strip()).load()

                except botocore.client.ClientError as e:
                    logging.warning(
                        "{}: {}.".format(uri.strip(), e.response["Error"]["Message"])
                    )
                    pass

                else:
                    try:
                        resp = requests.get(
                            "https://{}.s3.amazonaws.com/{}".format(
                                BUCKET, uri.strip()
                            ),
                            stream=True,
                        )
                    except Exception as e:
                        # ConnectionError: HTTPSConnectionPool
                        logging.error(
                            "Exception type: {}, Message: {}".format(
                                type(e).__name__, e
                            )
                        )
                        pass
                    else:

                        for record in ArchiveIterator(resp.raw, arc2warc=True):
                            if record.rec_headers["Content-Type"] == "application/json":

                                try:
                                    content = json.loads(record.content_stream().read())

                                except Exception as e:
                                    logging.warning(
                                        "JSON payload file: {}. Exception type: {}, Message: {}".format(
                                            uri.strip(), type(e).__name__, e
                                        )
                                    )
                                    pass

                                else:
                                    if (
                                        content["Envelope"]["WARC-Header-Metadata"][
                                            "WARC-Type"
                                        ]
                                        != "response"
                                    ):
                                        continue
                                    elif (
                                        "HTML-Metadata"
                                        not in content["Envelope"]["Payload-Metadata"][
                                            "HTTP-Response-Metadata"
                                        ]
                                    ):
                                        continue
                                    elif (
                                        "Links"
                                        not in content["Envelope"]["Payload-Metadata"][
                                            "HTTP-Response-Metadata"
                                        ]["HTML-Metadata"]
                                    ):
                                        continue

                                    try:
                                        segment = uri.split("/wat/")[0].strip()
                                        targetURI = urlparse(
                                            content["Envelope"]["WARC-Header-Metadata"][
                                                "WARC-Target-URI"
                                            ].strip()
                                        )
                                        offset = int(
                                            content["Container"]["Offset"].strip()
                                        )
                                        filename = content["Container"][
                                            "Filename"
                                        ].strip()
                                        dftLength = int(
                                            content["Container"]["Gzip-Metadata"][
                                                "Deflate-Length"
                                            ].strip()
                                        )

                                        links = filter(
                                            lambda x: "url" in x,
                                            content["Envelope"]["Payload-Metadata"][
                                                "HTTP-Response-Metadata"
                                            ]["HTML-Metadata"]["Links"],
                                        )

                                        result = map(
                                            lambda x: (
                                                targetURI.netloc,
                                                targetURI.path,
                                                targetURI.query,
                                                urlparse(x["url"]).netloc,
                                                urlparse(x["url"]).path,
                                                segment,
                                                filename,
                                                offset,
                                                dftLength,
                                                json.dumps(
                                                    {
                                                        "Images": len(
                                                            list(
                                                                set(
                                                                    map(
                                                                        lambda i: i[
                                                                            "url"
                                                                        ],
                                                                        filter(
                                                                            lambda z: "IMG@/src"
                                                                            in z[
                                                                                "path"
                                                                            ],
                                                                            links,
                                                                        ),
                                                                    )
                                                                )
                                                            )
                                                        ),
                                                        "Links": Counter(
                                                            map(
                                                                lambda l: urlparse(
                                                                    l["url"]
                                                                ).netloc,
                                                                filter(
                                                                    lambda z: "A@/href"
                                                                    in z["path"]
                                                                    and targetURI.netloc
                                                                    not in z["url"]
                                                                    and urlparse(
                                                                        z["url"]
                                                                    ).netloc
                                                                    != "",
                                                                    links,
                                                                ),
                                                            )
                                                        ),
                                                    }
                                                ),
                                            ),
                                            filter(
                                                lambda y: "creativecommons.org"
                                                in y["url"],
                                                links,
                                            ),
                                        )

                                    except (KeyError, ValueError) as e:
                                        logging.error(
                                            "{}:{}, File:{}".format(
                                                type(e).__name__, e, uri.strip()
                                            )
                                        )
                                        pass

                                    else:
                                        if result:
                                            yield from result

    def generateParquet(self, _data):
        """
        Create a parquet file with the extracted content.

        Parameters
        ------------------
        _data: generator
            A list containing the extracted domains and their associated meta-data.

        Returns
        ------------------
        None
        """

        schema = StructType(
            [
                StructField("provider_domain", StringType(), True),
                StructField("content_path", StringType(), True),
                StructField("content_query_string", StringType(), True),
                StructField("cc_domain", StringType(), True),
                StructField("cc_license", StringType(), True),
                StructField("warc_segment", StringType(), True),
                StructField("warc_filename", StringType(), True),
                StructField("content_offset", LongType(), True),
                StructField("deflate_length", LongType(), True),
                StructField("html_metadata", StringType(), True),
            ]
        )

        spk = SparkSession.builder.getOrCreate()
        df = spk.createDataFrame(_data, schema=schema)
        df.write.format("parquet").mode("overwrite").save(self.output)


def main():
    args = sys.argv[1]
    crawlIndex = args.strip()

    if crawlIndex.lower() == "--default":
        s3 = boto3.client("s3")

        # verify bucket
        contents = []
        prefix = "cc-index/collections/CC-MAIN-"
        botoArgs = {"Bucket": BUCKET, "Prefix": prefix}

        while True:

            objects = s3.list_objects_v2(**botoArgs)

            for obj in objects["Contents"]:
                key = obj["Key"]

                if "indexes" in key:
                    cIndex = key.split("/indexes/")[0].split("/")
                    cIndex = cIndex[len(cIndex) - 1]

                    if str(cIndex) not in contents:
                        contents.append(str(cIndex))

            try:
                botoArgs["ContinuationToken"] = objects["NextContinuationToken"]
            except KeyError:
                break

        if contents:
            crawlIndex = contents[-1]

    sc = SparkContext(appName="ExtractCCLinks")

    ccLinks = CCLinks(crawlIndex.upper(), sc.defaultParallelism)
    watPaths = ccLinks.loadWATFile()

    if watPaths is None:
        sc.stop()
        sys.exit()

    watRDD = sc.parallelize(watPaths, ccLinks.numPartitions)
    result = watRDD.mapPartitions(ccLinks.processFile)

    ccLinks.generateParquet(result)
    sc.stop()


if __name__ == "__main__":
    main()

# flake8: noqa
import argparse
import os
import re

import boto3
from botocore import UNSIGNED
from botocore.client import Config


BUCKET = os.environ["S3_BUCKET"]
COMMONCRAWL_BUCKET = os.environ.get("COMMONCRAWL_BUCKET", "not_set")
PATH = os.environ["OUTPUT_DIR"]
ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
SECRET_KEY = os.environ["AWS_SECRET_KEY"]


def getCrawlIndex(_param):

    if not _param:  # get the most recent index from common crawl
        s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))

        # verify bucket
        contents = []
        prefix = "cc-index/collections/CC-MAIN-"
        botoArgs = {"Bucket": COMMONCRAWL_BUCKET, "Prefix": prefix}

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
            _param = contents[-1]

    return _param


def validateIndexPattern(_index, _pattern=re.compile(r"CC-MAIN-\d{4}-\d{2}")):
    if not _pattern.match(_index):
        logging.error("Invalid common crawl index format => {}.".format(_index))
        raise argparse.ArgumentTypeError
    return _index


def syncS3Objects(_index):
    s3 = boto3.client(
        "s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY
    )
    botoArgs = {"Bucket": BUCKET, "Prefix": "common_crawl_image_data/{}".format(_index)}

    objects = s3.list_objects_v2(**botoArgs)

    for obj in objects.get("Contents", []):
        key = obj["Key"]

        if "_SUCCESS" not in key:
            fileName = key.lstrip("common_crawl_image_data/").replace("/", "_")
            fileName = "{}{}".format(PATH, fileName)
            fileName = fileName.replace(".csv", ".tsv")

            with open(fileName, "wb") as fh:
                s3.download_fileobj(BUCKET, key, fh)

                # check if the file exists locally before removing it from the s3 bucket
                if os.path.exists(fileName) and os.path.getsize(fileName) > 0:
                    s3.delete_object(Bucket=BUCKET, Key=key)
                    logging.info("Deleted object: {}".format(key))
        else:
            s3.delete_object(Bucket=BUCKET, Key=key)


def main():

    parser = argparse.ArgumentParser(
        description="Sync Common Crawl Image Providers", add_help=True
    )
    parser.add_argument("--index", type=validateIndexPattern)
    args = parser.parse_args()

    ccIndex = getCrawlIndex(args.index)
    syncS3Objects(ccIndex)

    logging.info("Terminated!")


if __name__ == "__main__":
    main()

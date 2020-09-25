"""
Script to merge the tags and metadata column from Common crawl data
to the new provider API data in image table.

Execution : python merge_cc_tags.py -c {cc_table_name} -a {api_table}

    eg : python merge_cc_tags.py -c science_museum_2020_06_02 -a image

"""
import os
import logging
import argparse
import psycopg2
from textwrap import dedent

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

COL_IMAGE = 'url'
COL_TAGS = 'tags'
COL_PROVIDER = 'provider'
COL_METADATA = 'meta_data'
CONNECTION_ID = os.getenv("AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING")


def _strip_url_schema(url):
    return f"""
            (
             CASE
             WHEN {url} SIMILAR TO 'https://%' THEN LTRIM({url}, 'https://')
             WHEN {url} SIMILAR TO 'http://%' THEN LTRIM({url}, 'http://')
             ELSE {url}
             END
            )
           """


def _modify_urls(
    url=None,
    provider_table=None
):
    if "museums_victoria" in provider_table:
        sub_query = f"""
                        SPLIT_PART({_strip_url_schema(url)}, '-', 1)
                     """

    elif "science_museum" in provider_table:
        sub_query = f"""
                        RTRIM(
                            SPLIT_PART(
                                REVERSE(
                            {_strip_url_schema(url)}
                        ), '/', 1), 'medium|large')
                     """

    elif "met" in provider_table:
        sub_query = f"""
                      SPLIT_PART(
                          REVERSE(
                            {_strip_url_schema(url)}
                          )
                      , '/', 1)
                     """
    return sub_query


def _merge_jsonb_objects(column):
    """
    This function returns SQL that merges the top-level keys of the
    a JSONB column, taking the newest available non-null value.
    """
    return f'''
            {column} = COALESCE(
                jsonb_strip_nulls(a.{column})
                    || jsonb_strip_nulls(b.{column}),
                a.{column},
                b.{column}
            )
            '''


def _merge_jsonb_arrays(column):
    return f'''{column} = COALESCE(
        (
            SELECT jsonb_agg(DISTINCT x)
            FROM jsonb_array_elements(a.{column} || b.{column}) t(x)
        ),
        a.{column},
        b.{column}
        )'''


def _merge_tags(
    cc_table=None,
    api_table=None
        ):
    try:
        status = "success"
        db = psycopg2.connect(
            CONNECTION_ID
        )
        cursor = db.cursor()
        query = dedent(
                f"""
                UPDATE {api_table} a
                    SET
                        {_merge_jsonb_arrays(COL_TAGS)},
                        {_merge_jsonb_objects(COL_METADATA)}
                FROM {cc_table} b
                WHERE
                a.{COL_PROVIDER} = b.{COL_PROVIDER}
                AND
                {_modify_urls('a.'+COL_IMAGE,
                            cc_table)} = {_modify_urls('b.'+COL_IMAGE,
                            cc_table)}
                """
        )
        cursor.execute(
            query
        )
        db.commit()
    except Exception as e:
        logger.warning(f"Merging failed due to {e}")
        status = "Failure"
    return status


def main(cc_table, api_table):
    logger.info(f"Merging Common crawl tags from {cc_table} to {api_table}")
    status = _merge_tags(
            cc_table=cc_table,
            api_table=api_table
            )
    logger.info(f"Status: {status}")


if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument(
        "-c", "--CC_table", required=True, help="Select Common crawl table"
    )
    parse.add_argument(
        "-a", "--API_table", required=True,
        help="Select table with new API data"
    )
    args = parse.parse_args()
    main(
        cc_table=args.CC_table,
        api_table=args.API_table
    )

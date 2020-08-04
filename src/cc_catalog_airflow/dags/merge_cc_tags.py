import os
import logging
import argparse
import psycopg2

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

IMAGE_TABLE_NAME = 'image'
COL_IMAGE = 'url'
COL_TAGS = 'tags'
COL_PROVIDER = 'provider'
COL_METADATA = 'meta_data'
CONNECTION_ID = os.getenv("AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING")


def _strip_url_schema(url):
    return f"""
            (
             CASE
             WHEN {url} like 'https://%' THEN LTRIM({url}, 'https://')
             WHEN {url} like 'http://%' THEN LTRIM({url}, 'http://')
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
                        SPLIT_PART()
                     """
    return sub_query


def _merge_jsonb_objects(column):
    """
    This function returns SQL that merges the top-level keys of the
    a JSONB column, taking the newest available non-null value.
    """
    return f'''
         {column} = COALESCE(
            b.{column},
            a.{column},
            jsonb_strip_nulls(a.{column})
                || jsonb_strip_nulls(b.{column})
        )
        '''


def _merge_jsonb_arrays(column):
    return f'''{column} = COALESCE(
        (
            SELECT jsonb_agg(DISTINCT x)
            FROM jsonb_array_elements(a.{column} || b.{column}) t(x)
        ),
        b.{column},
        a.{column}
        )'''


def _merge_tags(
    cc_table=None,
    image_table=IMAGE_TABLE_NAME
        ):
    try:
        status = "success"
        db = psycopg2.connect(
            CONNECTION_ID
        )
        cursor = db.cursor()
        api_links = []
        cc_links = []
        cursor.execute(
            f"""
            select {_modify_urls('a.' + COL_IMAGE, cc_table)} from {IMAGE_TABLE_NAME} a
            where  a.{COL_PROVIDER} = 'sciencemuseum'
            """
        )
        for i in cursor.fetchall():
            api_links.append(i[0])
        cursor.execute(
            f"""
            select {_modify_urls('b.' + COL_IMAGE, cc_table)} from {cc_table} b
            where  b.{COL_PROVIDER} = 'sciencemuseum'
            """
        )
        for j in cursor.fetchall():
            cc_links.append(j)
        # cursor.execute(
        # f"""
        #     UPDATE {IMAGE_TABLE_NAME} a
        #         SET
        #             {_merge_jsonb_arrays(COL_TAGS)},
        #             {_merge_jsonb_objects(COL_METADATA)}
        #     FROM {cc_table} b
        #     WHERE
        #     a.{COL_PROVIDER} = b.{COL_PROVIDER}
        #     AND
        #     {_modify_urls('a.'+COL_IMAGE,
        #                   cc_table)} = {_modify_urls('b.'+COL_IMAGE,
        #                   cc_table)}
        # """
        # )
        common_links = set(api_links).intersection(set(cc_links))
        print(len(common_links))
        for i in common_links:
            print(i)
    except Exception as e:
        logger.warning(f"Merging failed due to {e}")
        status = "Failure"
    return status


def main(cc_table):
    logger.info(f"Merging Common crawl tags from {cc_table}")
    status = _merge_tags(
            cc_table=cc_table
            )
    logger.info(f"Status: {status}")


if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument("-t", "--Table", required=True, help="Select table")
    args = parse.parse_args()
    main(cc_table=args.Table)

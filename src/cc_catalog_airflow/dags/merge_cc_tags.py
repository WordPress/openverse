"""
    Museum Victoria -- 
            API urls =     142532
            CC urls  =     81799
            Common   =      0


    Science Museum -- 
            API links =    62515
            CC url    =    67390
            Common    =    22228

    Met Museum :
            API links =    10574 (Did not run completely )
            CC urls   =    522488
            Common    =    9973

"""
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
            where  a.{COL_PROVIDER} = 'museumsvictoria'
            """
        )
        for i in cursor.fetchall():
            api_links.append(i[0])
        cursor.execute(
            f"""
            select {_modify_urls('b.' + COL_IMAGE, cc_table)} from {cc_table} b
            """
        )
        for j in cursor.fetchall():
            cc_links.append(j[0])
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
        print(len(api_links))
        print(len(cc_links))
        common_links = set(api_links).intersection(set(cc_links))
        print(len(common_links))
        # print(common_links)
        # for i in common_links:
        #     print(i)
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

"""
Science Museum - 
select RTRIM(SPLIT_PART(REVERSE(LTRIM(a.url, 'https://')), '/', 1), 'medium|large') as api_url, RTRIM(SPLIT_PART(REVERSE(LTRIM(b.url, 'https://')), '/', 1), 'medium|large') as cc_url from image as a , science_museum_2020_06_02 as b
where
RTRIM(SPLIT_PART(REVERSE(LTRIM(a.url, 'https://')), '/', 1), 'medium|large') = RTRIM(SPLIT_PART(REVERSE(LTRIM(b.url, 'https://')), '/', 1), 'medium|large') limit 20;



MET MUSEUM :
select distinct SPLIT_PART(REVERSE(LTRIM(a.url, 'https://')),'/', 1) as api_url from 
image as a, met_museum_2020_06_05 as b where SPLIT_PART(REVERSE(LTRIM(a.url, 'https://')),'/', 1)=SPLIT_PART(REVERSE(LTRIM(b.url, 'https://')),'/', 1) and a.provider='met' ;

"""
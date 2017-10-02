from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
from pyspark.sql.types import *
from pyspark.sql.functions import *
from gzipstream import GzipStreamFile
from boto.s3.key import Key
import json
import boto
import warc
import pytest


@pytest.fixture(scope="session")
def spark_context(request):
     conf = (SparkConf()
            .setMaster("local[2]")
            .setAppName("commonsmapper-pyspark-local-testing")
            )
     sc = SparkContext(conf=conf)
     request.addfinalizer(lambda: sc.stop())
     return sc

@pytest.fixture(scope="session")
def sql_context(request, spark_context):
    return SQLContext(spark_context)

def get_records(id_, iterator):
    conn = boto.connect_s3(anon=True, host='s3.amazonaws.com')
    bucket = conn.get_bucket('commoncrawl')

    for uri in iterator:
        key_ = Key(bucket, uri)
        _file = warc.WARCFile(fileobj=GzipStreamFile(key_))

        for record in _file:
            if record['Content-Type'] == 'application/json':
                record = json.loads(record.payload.read())
                try:
                    def cc_filter(x):
                        return "creativecommons.org" in x['url']

                    cc_links = filter(cc_filter, list(record['Envelope']['Payload-Metadata']['HTTP-Response-Metadata']['HTML-Metadata']['Links']))
                    if len(cc_links) > 0:
                        yield record
                except KeyError:
                    pass

@pytest.fixture(scope="session")
def wat_file(request,spark_context):
        files = spark_context.textFile("wat.paths.gz");
        records = files.mapPartitionsWithSplit(get_records) \
                #.map(lambda x: x) 
        return records

@pytest.fixture(scope="session")
def links(request,wat_file,sql_context):
    
    lns = wat_file.flatMap(lambda x: filter(lambda y: "creativecommons.org" in y['url'], x['Envelope']['Payload-Metadata']['HTTP-Response-Metadata']['HTML-Metadata']['Links']))\
            .map(lambda x: (x['url'], 1)) \
            .reduceByKey(lambda x, y: x + y)
    schema = StructType([
        StructField("deed_url", StringType(), True),
        StructField("link_count", LongType(), True)
    ])

    return sql_context.createDataFrame (lns, schema=schema)

@pytest.fixture(scope="session")
def save_to_hive(request, links, sql_context):
    print "Will save to Hive"


@pytest.mark.usefixtures("links")
def test_top_3(links):
    nl = list(links.sort(col('link_count').desc()).take(3))
    for l in nl:
        print (l)
        assert "creativecommons.org" in l['deed_url'] and l['link_count'] > 90

@pytest.mark.usefixtures("save_to_hive")
def test_save(save_to_hive):
    assert 0

@pytest.mark.usefixtures("wat_file")
def test_save_commons_warc (wat_file):
    assert 0

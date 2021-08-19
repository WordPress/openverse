from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
from pyspark.sql.types import *
from pyspark.sql.functions import *
from gzipstream import GzipStreamFile
from boto.s3.key import Key
from urlparse import urlparse
import json
import boto
import warc
import pytest
import os


@pytest.fixture(scope="session")
def spark_context(request):
     conf = (SparkConf()
            .setMaster("spark://ec2-54-167-211-230.compute-1.amazonaws.com:7077")
            .setAppName("commonsmapper-pyspark-local-testing")
            .set ("spark.jars", "../jars/hadoop-aws-2.8.1.jar,../jars/hadoop-auth-2.8.1.jar,../jars/aws-java-sdk-1.11.212.jar,../jars/postgresql-42.1.4.jar")
            .set ("spark.driver.extraClassPath", "../jars/")
            )
     sc = SparkContext(conf=conf)
     sc._jsc.hadoopConfiguration ().set("fs.s3n.awsAccessKeyId", os.environ ['OPEN_LEDGER_ACCESS_KEY_ID'])
     sc._jsc.hadoopConfiguration ().set("fs.s3n.awsSecretAccessKey", os.environ ['OPEN_LEDGER_SECRET_ACCESS_KEY'])
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
def data_by_deed(request,wat_file):
    def get_links (data):
        ret = []
        for link in data['links']:
            p = urlparse (link ['url'])
            if ("creativecommons.org" in p.netloc):
                ret.append ((p.path, data))
        return ret

    
    lns = wat_file.map(lambda x: {
        'data': x, 
        'uri': x ['Envelope']['WARC-Header-Metadata']['WARC-Target-URI'], 
        'links': filter(lambda y: "creativecommons.org" in y['url'], x['Envelope']['Payload-Metadata']['HTTP-Response-Metadata']['HTML-Metadata']['Links']),
        'value': 1,
        })\
        .flatMap(lambda x: get_links (x)) 
    return lns

@pytest.fixture(scope="session")
def deed_by_domain (request, data_by_deed, sql_context):
    def aggregate_by_domain (acc, item): 
        domain = urlparse(item ['uri']).netloc
        if (domain not in acc):
            acc [domain] = 0
        acc[domain] += 1
        return acc
    def flat (deed): 
        return map (lambda domain: (deed [0], domain, deed [1][domain]), deed [1])
        #ret = []
        #for domain in deed [1]:
        #    ret.append ((deed [0], domain, deed [1][domain]))
        #return ret;

    lns = data_by_deed.aggregateByKey ({}, aggregate_by_domain, lambda s, d: s + d).flatMap (lambda x: flat (x))

    return sql_context.createDataFrame (lns, ["license", "domain", "count"]);


@pytest.fixture(scope="session")
def links(request,data_by_deed, sql_context): 
    def reducer (accum, item): 
        a = accum if type(accum) is int else 1 
        return a + item ['value']

    lns = data_by_deed.aggregateByKey (0, reducer, lambda s1,d1: s1 + d1)

    schema = StructType([
        StructField("deed_url", StringType(), True),
        StructField("link_count", LongType(), True)
    ])

    return sql_context.createDataFrame (lns, schema=schema)

@pytest.fixture(scope="session")
def save_to_sql(request, links, sql_context):
    links.write\
            .jdbc ("jdbc:postgresql://localhost:5432/commonsmapper", "deeds_count", mode='overwrite', properties={'user': 'paw', 'password': ''})
    pass



#@pytest.mark.usefixtures("links")
#def test_top_3(links):
#    for l in links.sort(col('link_count').desc()).take(3):
#        print (l)
#        assert "licenses" in l['deed_url'] and l['link_count'] > 90

@pytest.mark.usefixtures("deed_by_domain")
def test_by_domain(deed_by_domain):
    deed_by_domain.write.format('csv').save("s3n://commonsmapper/licenses_by_domain/", mode='overwrite')
    pass

@pytest.mark.usefixtures("save_to_sql")
def test_save_commons_warc (save_to_sql):
    pass 

import logging
from MetMuseum import MetMuseum
from Flickr import Flickr
from MuseumVictoria import MuseumVictoria
from DeviantArt import DeviantArt
from GeographOrgUK import GeographOrgUK
from pyspark import SparkContext
import sys

logging.basicConfig(format='%(asctime)s - %(name)s: [%(levelname)s] =======> %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) < 2:
        logger.error('Invalid arguments provided.')
        logger.error('Provide the common crawl index.')
        sys.exit()

    args        = sys.argv[1]
    crawlIndex  = args.strip()

    if crawlIndex is None:
        sys.exit()


    crawlIndex = crawlIndex.upper()
    sc   = SparkContext(appName='Provider - Extract Image.')

    logger.info('Processing crawl index: {}'.format(crawlIndex))

    filePath = ''
    fh       = sc.textFile('{}providers.csv'.format(filePath)).collect()

    for line in fh:
        providerName, providerDomain = line.split(',')
        providerName, providerDomain = providerName.strip(), providerDomain.strip()
        provider                     = None
        data                         = None

        logger.info('Initializing {} job'.format(providerName))

        #Initialize each provider, load their data and filter urls to obtain the image collection
        if providerName == 'met':
            #The Met Museum Collection
            provider = MetMuseum(providerName, providerDomain, crawlIndex)
            data     = provider.filterData(provider.getData(), 'art/collection/')

        elif providerName == 'flickr':
            #Flickr Photo Collection
            provider    = Flickr(providerName, providerDomain, crawlIndex)
            data        = provider.filterData(provider.getData(), '/photos/')

        elif providerName == 'museumvictoria':
            #The Museums Victoria Collection
            provider    = MuseumVictoria(providerName, providerDomain, crawlIndex)
            data        = provider.filterData(provider.getData())

        elif providerName == 'deviantart':
            #The Deviant Art Collection
            provider    = DeviantArt(providerName, providerDomain, crawlIndex)
            data        = provider.filterData(provider.getData(), '/art/')

        elif providerName == 'geographorguk':
            #Geograph.org photos
            provider    = GeographOrgUK(providerName, providerDomain, crawlIndex)
            data        = provider.filterData(provider.getData(), '/photo/')

        else:
            continue



        if data:
            rdd  = sc.parallelize(data, sc.defaultParallelism)

            if provider and (not rdd.isEmpty()):
                result = rdd.mapPartitions(provider.extractHTML)
                if (not result.isEmpty()):
                    provider.saveData(result)


    sc.stop()


if __name__ == '__main__':
    main()

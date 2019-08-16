# Creative Commons Catalog
*Mapping the commons towards an open ledger and cc search.*

## Description
This repository contains the methods used to identify over 1.4 billion Creative Commons licensed works. The challenge is that these works are dispersed throughout the web and identifying them requires a combination of techniques. Two approaches are currently being explored:
1. [Web crawl data](#web-crawl-data)
2. [Application Programming Interfaces (APIs)](#application-programming-interfaces-apis)

### Web Crawl Data
The Common Crawl Foundation provides an open repository of petabyte-scale web crawl data. A new dataset is published at the end of each month comprising over 200 TiB of uncompressed data. 

The data is available in three formats:
- WARC: the entire raw data, including HTTP response metadata, WARC metadata, etc.
- WET: extracted plaintext from each webpage.
- WAT: extracted html metadata, e.g. HTTP headers and hyperlinks, etc.

CC Catalog uses AWS Data Pipeline service to automatically create an EMR cluster of 100 c4.8xlarge instances that will parse the WAT archives to identify all domains that link to creativecommons.org. Due to the volume of data, Apache Spark is used to streamline the processing. The output of this methodology is a series of parquet files that contain:
- the domains and its respective content path and query string (i.e. the exact webpage that links to creativecommons.org)
- the CC referenced hyperlink (which may indicate a license), 
- HTML meta data in JSON format which indicates the number of images on each webpage and other domains that they reference, 
- the location of the webpage in the WARC file so that the page contents can be found.

The steps above are performed in [ExtractCCLinks.py](https://github.com/creativecommons/cccatalog/blob/master/src/ExtractCCLinks.py)

### Application Programming Interfaces (APIs)


## Getting Started

### Prerequisites
```
JDK 9.0.1
Python 2.7
Spark 2.2.0

pip install -r requirements.txt
```

## Running the tests
```
python -m unittest discover -v
```

## Authors
See the list of [contributors](https://github.com/creativecommons/cccatalog/contributors) who participated in this project.

## License
This project is licensed under the MIT license - see the [LICENSE](LICENSE) file for details.

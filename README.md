# Creative Commons Catalog
*Mapping the commons towards an open ledger and cc search.*

## Description
This repository contains the methods used to identify over 1.4 billion Creative Commons licensed works. The challenge is that these works are dispersed throughout the web and identifying them requires a combination of techniques. Two approaches are currently being explored:
* Web crawl data, and
* Application Programming Interfaces (APIs)

### Web Crawl Data
The Common Crawl Foundation provides a repository of free web crawl data that is stored on Amazon Public Datasets. At the begining of each month, we process their most recent meta-data to identify all domains that link to Creative Commons. Due to the volume of data, Apache Spark is used to streamline the processing.

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

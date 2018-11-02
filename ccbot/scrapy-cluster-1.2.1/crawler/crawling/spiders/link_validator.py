from __future__ import absolute_import
from scrapy.http import Request

from crawling.items import LinkValidationInfo, RawResponseItem
from crawling.spiders.redis_spider import RedisSpider


class LinkValidatorSpider(RedisSpider):
    """
    A crawler that uses HTTP HEAD requests to validate that links exist.
    """
    name = "validator"

    def __init__(self, *args, **kwargs):
        super(LinkValidatorSpider, self).__init__(*args, **kwargs)

    def make_requests_from_url(self, url):
        return Request(url, method='HEAD', dont_filter=True)

    def parse(self, response):
        self._logger.debug("crawled url {}".format(response.request.url))
        # capture raw response
        item = RawResponseItem()
        # populated from response.meta
        item['appid'] = response.meta['appid']
        item['crawlid'] = response.meta['crawlid']
        item['attrs'] = response.meta['attrs']

        # populated from raw HTTP response
        item["url"] = response.request.url
        item["response_url"] = response.url
        item["status_code"] = response.status
        item["response_headers"] = self.reconstruct_headers(response)
        item["request_headers"] = response.request.headers

        # raw response has been processed, yield to item pipeline
        self._logger.debug("Created Item successfully")
        yield item

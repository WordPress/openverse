## What is this?

A distributed solution for retrieving images from a list of URLs fed to a 
message queue. Scrapy spider(s) consume messages from this queue and 
store the images at the configured resolution.

## How do I start it?
`docker-compose up`

## How do I feed images to it?
Add URLs to the incoming image topic.

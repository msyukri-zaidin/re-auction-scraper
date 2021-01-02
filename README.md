# Real Estate Auction Scraper

Web scraper that extracts data from http://house.speakingsame.com/

## Usage
```
scrapy crawl posts -a suburb=[suburb name]
```
This command will scrape all pages for the provided suburb.

```
scrapy crawl posts -a proxy=check
```
This command performs a connection check. Useful for ensuring proxies are working.

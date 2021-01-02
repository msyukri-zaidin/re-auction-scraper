# Real Estate Auction Scraper

Web scraper that extracts data from http://house.speakingsame.com/

## Getting Started

Firstly, ensure that you have Anaconda installed.

Then, install the packages

```
conda env create -f environment.yml
```

## Usage
This command will scrape all pages for the provided suburb.
```
scrapy crawl posts -a suburb=[suburb name]
```

This command performs a connection check. Useful for ensuring proxies are working.
```
scrapy crawl posts -a proxy=check
```

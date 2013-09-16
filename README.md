ESEA Scraper (TF2)
==================

Scrapes data from the ESEA website for all Team Fortress 2 matches in Seasons 9-14, from
June 26, 2011 to September 6, 2011. This project uses Python and the web crawling/scraping
framework Scrapy.

Instructions
------------

You will need Python 2.7.x and pip. To install the dependencies,

```
pip install -r requirements.txt
```

To run the spider and write data to the file `matches.jsonlines` (a file format with one
JSON object on each line),

```
scrapy crawl play.esea.net -o matches.jsonlines -t jsonlines
``` 

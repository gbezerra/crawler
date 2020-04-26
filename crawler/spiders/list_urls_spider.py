from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.http import Request

DOMAIN = 'liquor.com'
URL = 'https://%s' % DOMAIN


class MySpider(BaseSpider):
    name = DOMAIN
    allowed_domains = [DOMAIN]
    start_urls = [
        URL
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        for url in hxs.select('//a/@href').extract():
            if not (url.startswith('http://') or url.startswith('https://')):
                url = URL + url

            if (url.startswith("https://www.liquor.com/recipes/")):
                print(url)
                with open('../urls.txt', 'a') as f:
                    f.write(url + '\n')
            yield Request(url, callback=self.parse)

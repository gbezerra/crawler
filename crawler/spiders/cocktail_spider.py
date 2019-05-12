import scrapy
import pdb
from bs4 import BeautifulSoup
import re

class CocktailSpider(scrapy.Spider):
    name = "cocktails"

    def __init__(self):
        super(CocktailSpider, self).__init__()
        self.counter = 0
        self.base_url = 'https://www.liquor.com/recipes/'

    def start_requests(self):
        urls = [
            self.base_url,
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse_ingredient(self, text):
        text = text.replace('\xa0', ' ')
        patterns =  [['oz', r"([\d\⁄\s]+)\s+oz\s+(.+)"],
        ['tsp', r"([\d\⁄\s]+)\s+tsp\s+(.+)"],
        ['pinch', r"([\d\⁄\s]+)\s+pinch\s+(.+)"],
        ['scoop', r"([\d\⁄\s]+)\s+scoop\s+(.+)"],
        ['leaves', r"([\d\⁄\s]+)\s+(leaves|leaf)\s+(.+)"],
        ['splashes', r"([\d\⁄\s]+)\s+(splash|splashes)\s+(.+)"],
        ['dashes', r"([\d\⁄\s]+)\s+(dashes|dash)\s+(.+)" ],
        ['top', r"\s*(.+),\s+to\s+(t|T)op"],
        ['rinse', r"\s*(.+),\s+to\s+rinse"],
        ['splash', r'.*Splash of (.+)'],
        ['whole', r"([\d\⁄\s]+)\s+(.+)"],
        ]
        ingredient = {}
        for unit, expr in patterns:
            result = re.match(expr, text)
            if result:
                if unit in ('oz', 'dashes', 'tsp', 'pinch', 'leaves', 'splashes', 'scoop'):
                    ingredient['quantity'] = result.group(1).strip()
                    ingredient['item'] = result.group(2).strip()
                    ingredient['unit'] = unit
                elif unit in ('top', 'splash', 'rinse'):
                    ingredient['quantity'] = None
                    ingredient['item'] = result.group(1).strip()
                    ingredient['unit'] = unit
                elif unit in ('whole'):
                    ingredient['quantity'] = result.group(1).strip()
                    ingredient['item'] = result.group(2).strip()
                    ingredient['unit'] = None
                break
        if 'quantity' not in ingredient:
            pdb.set_trace()
        print('ingredient:', ingredient)
        yield ingredient
        
        

    def parse_cocktail(self, response):
        #pdb.set_trace()
        for ingredient in response.css('div.col-xs-3.text-right').css('div.hide').getall():
            soup = BeautifulSoup(ingredient)
            text = soup.get_text()
            print(text)
            self.parse_ingredient(text)
            
            #yield {
            #    'name': quote.css('span.text::text').get(),
            #} 
            #print("\nIngredient:", ingredient)
        #pdb.set_trace()

    def parse(self, response):
        print("got response")
        for url in response.css('a.overlay::attr(href)').getall():
            print("url", self.base_url + url)
            #pdb.set_trace()
            yield scrapy.Request(url=self.base_url + url, callback=self.parse_cocktail)
        if self.counter < 44:
            self.counter += 1
            url = self.base_url + '/page/' + str(self.counter) + '/'
            yield scrapy.Request(url=url, callback=self.parse)
            
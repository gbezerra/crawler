import scrapy
import pdb
from bs4 import BeautifulSoup
import re
import json


class CocktailSpider(scrapy.Spider):
    name = "cocktails"

    def __init__(self):
        super(CocktailSpider, self).__init__()
        self.base_url = 'https://www.liquor.com/recipes/'

    def start_requests(self):
        urls = [
            self.base_url,
        ]
        for i in range(1, 45):
            urls.append(self.base_url + '/page/' + str(i) + '/')

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse_ingredient(self, text):

        def parse_quantity(text):
            expr = text.replace(' ', '+').replace('⁄', '/')
            quantity = eval(expr)
            return quantity

        text = text.replace('\xa0', ' ')
        patterns = [['oz', r"([\d\⁄\s]+)\s+oz\s+(.+)"],
                    ['tsp', r"([\d\⁄\s]+)\s+tsp\s+(.+)"],
                    ['pinch', r"([\d\⁄\s]+)\s+pinch\s+(.+)"],
                    ['scoop', r"([\d\⁄\s]+)\s+scoop\s+(.+)"],
                    ['leaves', r"([\d\⁄\s]+)\s+(leaves|leaf)\s+(.+)"],
                    ['splashes', r"([\d\⁄\s]+)\s+(splash|splashes)\s+(.+)"],
                    ['dashes', r"([\d\⁄\s]+)\s+(dashes|dash)\s+(.+)"],
                    ['top', r"\s*(.+),\s+to\s+(t|T)op"],
                    ['rinse', r"\s*(.+),\s+to\s+rinse"],
                    ['mist', r"\s*(.+),\s+to\s+mist"],
                    ['coating', r"\s*(.+),\s+for\s+coating"],
                    ['drizzling', r"\s*(.+),\s+for\s+drizzling"],
                    ['serving', r"\s*(.+),\s+for\s+serving"],
                    ['splash', r'.*Splash of (.+)'],
                    ['whole', r"([\d\⁄\s]+)\s+(.+)"],
                    ]
        ingredient = {}
        for unit, expr in patterns:
            result = re.match(expr, text)
            if result:
                if unit in ('oz', 'dashes', 'tsp', 'pinch', 'leaves', 'splashes', 'scoop'):
                    ingredient['quantity'] = result.group(
                        1).strip().replace('⁄', '/')
                    ingredient['item'] = result.group(2).strip()
                    ingredient['unit'] = unit
                elif unit in ('top', 'splash', 'rinse', 'coating', 'drizzling', 'serving', 'mist'):
                    ingredient['quantity'] = None
                    ingredient['item'] = result.group(1).strip()
                    ingredient['unit'] = unit
                elif unit in ('whole'):
                    ingredient['quantity'] = result.group(
                        1).strip().replace('⁄', '/')
                    ingredient['item'] = result.group(2).strip()
                    ingredient['unit'] = None
                break

        if 'quantity' not in ingredient:
            ingredient['quantity'] = None
            ingredient['item'] = text.split(',')[0].strip()
            ingredient['unit'] = None
        print('ingredient:', ingredient)
        return ingredient

    def parse_cocktail(self, response):
        # parse cocktail name
        name = response.css('div.col-xs-12').css('h1').get()
        name = BeautifulSoup(name).get_text()
        print('cocktail name:', name)

        # parse ingredients
        ingredient_list = []
        for ingredient in response.css('div.col-xs-3.text-right').css('div.hide').getall():
            soup = BeautifulSoup(ingredient)
            text = soup.get_text()
            print(text)
            ingredient_list.append(self.parse_ingredient(text))

        # parse garnish
        garnish_list = []
        for garnish in set(response.css('div.row.x-recipe-garnish').css('span.oz-value').getall()):
            soup = BeautifulSoup(garnish)
            text = soup.get_text()
            print('Garnish:', text)
            garnish_list.append(text.strip())

        # parse glass
        glass = response.css('div.row.x-recipe-glasstype').css('a::text').get()

        # parse preparation
        preparation = '\n'.join(response.css(
            'div.row.x-recipe-prep').css('p::text').getall())

        # parse image url
        image_url = response.css(
            'img.wp-post-image.img-responsive::attr(src)').get()

        # write contents to file
        cocktail = {'name': name,
                    'ingredients': ingredient_list,
                    'garnish': garnish_list,
                    'glass': glass,
                    'preparation': preparation,
                    'imageURL': image_url}
        with open('../output/' + name + '.json', 'w') as f:
            json.dump(cocktail, f)

    def parse(self, response):
        print("got response")
        for url in response.css('a.overlay::attr(href)').getall():
            print("url", self.base_url + url)
            # pdb.set_trace()
            yield scrapy.Request(url=self.base_url + url, callback=self.parse_cocktail)

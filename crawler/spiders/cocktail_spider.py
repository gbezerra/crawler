import scrapy
import pdb
from bs4 import BeautifulSoup
import re
import json


class CocktailSpider(scrapy.Spider):
    name = "cocktails"
    handle_httpstatus_list = [301]

    def __init__(self):
        super(CocktailSpider, self).__init__()

    def start_requests(self):
        with open("../urls.txt") as f:
            urls = f.readlines()
        urls = [e[:-1] for e in urls]

        additional_urls = ['https://www.liquor.com/recipes/teeling-butter-and-scotch-irish-coffee/',
                           "https://www.liquor.com/recipes/bourbon-old-fashioned/",
                           "https://www.liquor.com/recipes/mollymock/",
                           "https://www.liquor.com/recipes/vanilla-orangecello/",
                           "https://www.liquor.com/recipes/aberlour-number-402/"]
        for url in urls[:0] + additional_urls:
            print("URL starting:", url)
            yield scrapy.Request(url=url, callback=self.parse_cocktail)

    def parse_ingredient(self, text):

        def parse_quantity(text):
            expr = text.replace(' ', '+').replace('⁄', '/')
            quantity = eval(expr)
            return quantity

        # print(text)

        ingredient = {}

        # handle garnish
        if text.startswith("Garnish:"):
            text = text.replace("Garnish:", '')
            ingredient['quantity'] = ""
            ingredient['item'] = text.split(',')[0].strip()
            ingredient['unit'] = ""
            ingredient['isGarnish'] = True
            return ingredient

        # handle ingrients
        text = text.replace('\xa0', ' ').replace('⁄', '/').lower()
        pattern1 = [['oz', r"([\d\/\s]+)\s+(oz|ounce|ounces)\s+(.+)"],
                    ['dashes', r"([\d\/\s]+)\s+(dashes|dash)\s+(.+)"],
                    ['tsp', r"([\d\/\s]+)\s+(tsp)\s+(.+)"],
                    ['cup', r"([\d\/\s]+)\s+(cup|cups)\s+(.+)"],
                    ['pinch', r"([\d\/\s]+)\s+(pinch)\s+(.+)"],
                    ['scoop', r"([\d\/\s]+)\s+(scoop|scoops)\s+(.+)"],
                    ['parts', r"([\d\/\s]+)\s+(part|parts)\s+(.+)"],
                    ['bsp', r"([\d\/\s]+)\s+(bsp|barspoon|barspoons)\s+(.+)"],
                    ['bottle', r"([\d\/\s]+)\s+(bottle|bottles)\s+(.+)"],
                    ]

        pattern2 = [
            ['top', r"\s*(.+),\s+to\s+(t|T)op"],
            ['rinse', r"\s*(.+),\s+to\s+rinse"],
            ['mist', r"\s*(.+),\s+to\s+mist"],
            ['coating', r"\s*(.+),\s+for\s+coating"],
            ['drizzling', r"\s*(.+),\s+for\s+drizzling"],
            ['serving', r"\s*(.+),\s+for\s+serving"],
        ]

        pattern3 = [['whole', r"([\d\/\s]+)\s+(.+)"], ]

        result = None
        for unit, expr in pattern1:
            result = re.match(expr, text)
            if result:
                ingredient['quantity'] = result.group(
                    1).strip()
                ingredient['item'] = result.group(3).strip()
                ingredient['unit'] = unit
                break
        if not result:
            for unit, expr in pattern2:
                result = re.match(expr, text)
                if result:
                    ingredient['quantity'] = ""
                    ingredient['item'] = result.group(1).strip()
                    ingredient['unit'] = unit
                    break

        if not result:
            for unit, expr in pattern3:
                result = re.match(expr, text)
                if result:
                    ingredient['quantity'] = result.group(
                        1).strip()
                    ingredient['item'] = result.group(2).strip()
                    ingredient['unit'] = ""
                    break

        if 'quantity' not in ingredient:
            ingredient['quantity'] = ""
            ingredient['item'] = text.split(',')[0].strip()
            ingredient['unit'] = ""
            ingredient['isGarnish'] = False
        return ingredient

    def parse_cocktail(self, response):

        # parse cocktail name
        soup = BeautifulSoup(response.text, 'html.parser')
        name = soup.find('h1', {'class': 'heading__title'}).get_text()
        print('cocktail name:', name)

        # parse ingredients
        ingredient_list = []
        ingredients = soup.findAll('li', {'class': 'simple-list__item'})
        for ing in ingredients:
            ing = self.parse_ingredient(ing.get_text().strip())
            ingredient_list.append(ing)
            #print('ingredient:', ing)

        # parse preparation
        preparation_text = []
        preparation = soup.findAll('div', {'class': 'mntl-sc-block-html'})
        for prep in preparation:
            prep = prep.get_text().strip()
            preparation_text.append(prep)
        preparation_text = '\n\n'.join(preparation_text)
        print(preparation_text)

        # parse image url
        image = soup.find('img', {'class': 'primary-image'})
        image = image['src']

        # # write contents to file
        # cocktail = {'name': name,
        #             'ingredients': ingredient_list,
        #             'garnish': garnish_list,
        #             'glass': glass,
        #             'preparation': preparation,
        #             'imageURL': image_url}
        # with open('../output/' + name + '.json', 'w') as f:
        #     json.dump(cocktail, f)

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
                           "https://www.liquor.com/recipes/aberlour-number-402/",
                           "https://www.liquor.com/recipes/vodka-red-bull/"]
        for url in urls:  # [:10] + additional_urls:
            print("URL starting:", url)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse_ingredient(self, text):

        ingredient = {}

        # handle garnish
        if text.startswith("Garnish:"):
            text = text.replace("Garnish:", '')
            ingredient['quantity'] = ""
            ingredient['name'] = text.split(',')[0].strip()
            ingredient['unit'] = ""
            ingredient['isGarnish'] = True
            return ingredient

        # handle ingrients
        text = text.replace('\xa0', ' ').replace('⁄', '/')
        pattern1 = [['oz', r"([\d\/\s]+)\s+(oz|ounce|ounces|Ounce|Ounces)\s+(.+)"],
                    ['dashes',
                        r"([\d\/\s]+)\s+(dashes|dash|Dash|Dashes)\s+(.+)"],
                    ['tsp', r"([\d\/\s]+)\s+(tsp)\s+(.+)"],
                    ['tbsp', r"([\d\/\s]+)\s+(tbsp)\s+(.+)"],
                    ['cup', r"([\d\/\s]+)\s+(cup|cups|Cup|Cups)\s+(.+)"],
                    ['pinch', r"([\d\/\s]+)\s+(pinch|Pinch)\s+(.+)"],
                    ['scoop', r"([\d\/\s]+)\s+(scoop|scoops|Scoop|Scoops)\s+(.+)"],
                    ['parts', r"([\d\/\s]+)\s+(part|parts|Part|Parts)\s+(.+)"],
                    ['bsp', r"([\d\/\s]+)\s+(bsp|barspoon|barspoons|Barspoon|Barspoons)\s+(.+)"],
                    ['bottle',
                        r"([\d\/\s]+)\s+(bottle|bottles|Bottle|Bottles)\s+(.+)"],
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
                ingredient['name'] = result.group(3).strip()
                ingredient['unit'] = unit
                break
        if not result:
            for unit, expr in pattern2:
                result = re.match(expr, text)
                if result:
                    ingredient['quantity'] = ""
                    ingredient['name'] = result.group(1).strip()
                    ingredient['unit'] = unit
                    break

        if not result:
            for unit, expr in pattern3:
                result = re.match(expr, text)
                if result:
                    ingredient['quantity'] = result.group(
                        1).strip()
                    ingredient['name'] = result.group(2).strip()
                    ingredient['unit'] = ""
                    break

        if 'quantity' not in ingredient:
            ingredient['quantity'] = ""
            ingredient['name'] = text.split(',')[0].strip()
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
        # print(preparation_text)

        # parse image url
        image = soup.find('img', {'class': 'primary-image'})
        image = image['src']

        # parse star rating
        try:
            review_count = soup.find(
                'div', {'class': 'aggregate-star-rating__count'}).get_text()
            review_count = int(review_count.split()[0])
            #print("Review count:", review_count)
            rating = len(soup.findAll('a', {'class': 'active'}))
            rating += len(soup.findAll('a', {'class': 'half'})) / 2
            #print("Rating:", rating)
        except:
            review_count = None
            rating = None

        # parse author name
        try:
            author_name = soup.find(
                'span', {'class': 'mntl-byline__span'}).get_text().strip()
        except:
            author_name = soup.find('div', {"id": "mntl-byline__name_1-0"}).find(
                'span', {'class': "link__wrapper"}).get_text().strip()
        #print("author name:", author_name)

        # write contents to file
        cocktail = {'name': name,
                    'ingredients': ingredient_list,
                    'preparation': preparation_text,
                    'imageURL': image,
                    'authorName': author_name,
                    'reviewCount': review_count,
                    'avgRating': rating}

        return cocktail

    def parse(self, response):
        filename = response.url.split('/')[-2]
        try:
            cocktail = self.parse_cocktail(response)
            with open('../output/' + filename + '.json', 'w') as f:
                json.dump(cocktail, f)
            with open('../successful_urls.txt', 'a') as f:
                f.write(response.url + '\n')
        except:
            with open('../unsuccessful_urls.txt', 'a') as f:
                f.write(response.url + '\n')

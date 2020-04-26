from os import listdir
from os.path import isfile, join
import re

raw_names = []
parsed_names = []
path = "/Users/gbezerra/OneDrive/George/Documents/Projects/CocktailApprentice/crawler/output/"
for filename in listdir(path):
    if filename.endswith('.json'):
        filename = filename[:-5]

        raw_names.append(filename)
        parsed = re.sub(r'[^a-zA-Z0-9_ \-]+', '',
                        filename).lower().replace(' ', '-')
        parsed_names.append(parsed)
        print(filename)
        print(parsed)
        print()

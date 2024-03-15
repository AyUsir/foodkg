import argparse
import os
import json
import random
import ssl
from SPARQLWrapper import SPARQLWrapper, JSON

from config.data_config import *
from utils.io_utils import *

def fetch_all_dishes(sparql):
    query = '''
        PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        SELECT DISTINCT ?r ?name {
            ?r a recipe-kb:recipe .
            ?r rdfs:label ?name .
        }'''

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    dishes = [(x['r']['value'], x['name']['value']) for x in results['results']['bindings']]
    print(len(dishes))
    return dishes

def fetch_all_ingredients(sparql, dish):
    query = '''PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        SELECT ?in {{
            {} recipe-kb:uses ?ii .
            ?ii recipe-kb:ing_name ?in
            OPTIONAL {{ ?ii recipe-kb:ing_quantity ?quantity . }}
            OPTIONAL {{ ?ii recipe-kb:ing_unit ?unit . }}
        }}
    '''.format(dish)

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    ingredients = [{
        'name': x['in']['value'],
        'quantity': x['quantity']['value'] if 'quantity' in x else None,
        'unit': x['unit']['value'] if 'unit' in x else None
    } for x in results['results']['bindings']]
    return ingredients


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', required=True, type=str, help='path to the output dir')
    opt = vars(parser.parse_args())

    ssl._create_default_https_context = ssl._create_unverified_context
    sparql = SPARQLWrapper(USE_ENDPOINT_URL)

    f_kg = open(os.path.join(opt['output'], 'recipe_kg.json'), 'w')
    dishes = fetch_all_dishes(sparql)
    i = 0
    for dish, dish_name in dishes:
        print(i+1)
        i = i+1
        dish_uri = dish 
        dish_name = dish_name 
        graph = {dish_uri: {'name': [dish_name], 'uri': dish_uri, 'alias': [], 'type': ['dish_recipe'], 'neighbors': {}}}
        graph[dish_uri]['neighbors']['contains_ingredients'] = []
        ingredients = fetch_all_ingredients(sparql, '<{}>'.format(dish_uri))
        for ingredient in ingredients:
            ingredient_name = ' '.join(ingredient['name'].split('/')[-1].split('%20'))
            ingredient_quantity = ingredient['quantity']
            ingredient_unit = ingredient['unit']
            ingredient_graph = {ingredient['name']: {'name': [ingredient_name], 'uri': ingredient['name'], 'alias': [], 'type': ['ingredient'],'quantity':ingredient_quantity,'unit':ingredient_unit}}
            graph[dish_uri]['neighbors']['contains_ingredients'].append(ingredient_graph)
        f_kg.write(json.dumps({dish_uri: graph}) + '\n')
        f_kg.flush()
    
    f_kg.close()
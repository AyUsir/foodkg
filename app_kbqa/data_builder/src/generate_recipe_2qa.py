import argparse
import os
from collections import defaultdict
import numpy as np

from utils.io_utils import *
from config.data_config import *


def add_qas_id(all_qas, dtype, seed=1234):
    width = len(str(len(all_qas))) + 1
    np.random.seed(seed)
    np.random.shuffle(all_qas)
    for i, qas in enumerate(all_qas):
        qas['qId'] = '{}-qas-{}-'.format(qas['qType'], dtype) + ('{0:0%sd}' % width).format(i)

def convert_to_standard_unit(quantity, unit):
    unit_conversion = {
        "cup": 240,    # Conversion to milliliters
        "tablespoon": 15,
        "teaspoon": 5,
        "lb": 453.592, # Conversion to grams
        "oz": 28.3495,
    }
    
    if unit in unit_conversion:
        standard_quantity = eval(quantity) * unit_conversion[unit]
        return standard_quantity
    else:
        return None


def generate_simple_qas(kg, kg_keys, simple_qas_templates, p=0.1, seed=1234):
    all_qas = []
    for recipe_uri in kg_keys:
        recipe_name = kg[recipe_uri]['name'][0]
        ingredients = kg[recipe_uri]['neighbors']['contains_ingredients']
        for ingredient in ingredients:
            ingredient = list(ingredient.values())[0]
            ingredient_name = ingredient['name'][0]
            quantity = ingredient['quantity']
            unit = ingredient['unit']
            if np.random.binomial(1, p, 1)[0] == 0 or not quantity or not unit:
                continue
            qas_template = np.random.choice(simple_qas_templates)
            qas_str = qas_template.format(s=recipe_name, p=ingredient_name)
            qas = {}
            qas['answers'] = [f"{quantity} {unit}"]
            qas['entities'] = [(recipe_name, 'recipe'),(ingredient_name,'ingredient')]
            qas['topicKey'] = [recipe_name]
            qas['rel_path'] = ['contains_ingredients']
            qas['qText'] = qas_str
            qas['qType'] = 'simple'
            all_qas.append(qas)
    return all_qas

def generate_comparision_qas(kg, kg_keys, comparision_qas_templates, p=0.1, seed=1234):
    all_qas = []
    ingredient_usage = defaultdict(dict)
    for recipe_uri in kg_keys:
        recipe_name = kg[recipe_uri]['name'][0]
        ingredients = kg[recipe_uri]['neighbors']['contains_ingredients']
        for ingredient in ingredients:
            ingredient = list(ingredient.values())[0]
            ingredient_name = ingredient['name'][0]
            quantity = ingredient['quantity']
            unit = ingredient['unit']
            standard_quantity = covert_to_standard_unit(quantity,unit)
            ingredient_usage[ingredient_name][recipe_name] = standard_quantity
    for ingredient_name , recipes in ingredient_usage.items():
        if len(recipes) < 2:
            continue
        recipe_names = list(recipes.keys())
        quantities = list(recipes.values())
        for i in range(len(recipe_names) - 1):
            for j in range(i+1,len(recipe_names)):
                if np.random.binomial(1, p, 1)[0] == 0:
                    continue
                recipe1,quantity1 = recipe_names[i],quantities[i]
                recipe2,quantity2 = recipe_names[j],quantities[j]
                qas_template = np.random.choice(comparision_qas_templates)
                qas_str = qas_template.format(s1=recipe1, s2=recipe2,p=ingredient_name)
                qas = {}
                qas['answers'] = [recipe1 if quantity1 > quantity2 else recipe2] 
                qas['intermediate_answers'] = [[str(quantity1)], [str(quantity2)]]
                qas['entities'] = [(ingredient_name, 'ingredient'), (recipe1, 'recipe'),(recipe2,'recipe')]
                qas['topicKey'] = [recipe1, recipe2,ingredient_name]
                qas['rel_path'] = ['contains_ingredients']
                qas['qText'] = qas_str
                qas['qType'] = 'comparison'
                all_qas.append(qas)
    return all_qas


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-recipe', '--recipe', type=str, help='path to the recipe data')
    parser.add_argument('-o', '--output', required=True, type=str, help='path to the output dir')
    parser.add_argument('-split_ratio', '--split_ratio', nargs=3, type=float, default=[0.5, 0.2, 0.3], help='split ratio')
    parser.add_argument('-sampling_prob', '--sampling_prob', default=0.05, type=float, help='sampling prob')

    opt = vars(parser.parse_args())

    train_ratio, valid_ratio, test_ratio = opt['split_ratio']
    assert sum(opt['split_ratio']) == 1

    np.random.seed(1234)

    # Recipe data
    recipe_kg = load_ndjson(opt['recipe'], return_type='dict')
    recipe_keys = list(recipe_kg.keys())


    # USDA simple questions
    simple_qas = generate_simple_qas(recipe_kg, recipe_keys, SIMPLE_QAS_TEMPLATES, p=opt['sampling_prob'])

    # USDA comparison questions
    comparision_qas = generate_comparision_qas(recipe_kg, recipe_keys, COMPARISION_QAS_TEMPLATES, p=opt['sampling_prob'])

    qas = simple_qas + comparision_qas


    train_size = int(len(qas) * train_ratio)
    valid_size = int(len(qas) * valid_ratio)
    test_size = len(qas) - train_size - valid_size

    np.random.shuffle(qas)


    train_qas = qas[:train_size]
    valid_qas = qas[train_size:train_size + valid_size]
    test_qas = qas[-test_size:]

    add_qas_id(train_qas, 'train')
    add_qas_id(valid_qas, 'valid')
    add_qas_id(test_qas, 'test')

    print('{} simple questions'.format(len(simple_qas)))
    print('{} comparison questions'.format(len(comparision_qas)))

    dump_ndjson(train_qas, os.path.join(opt['output'], 'train_qas.json'))
    dump_ndjson(valid_qas, os.path.join(opt['output'], 'valid_qas.json'))
    dump_ndjson(test_qas, os.path.join(opt['output'], 'test_qas.json'))
    print('Generated totally {} qas, training size: {}, validation size: {}, test size: {}'.format(train_size + valid_size + test_size, train_size, valid_size, test_size))
    print('Saved qas to {}'.format(opt['output']))

import re
import json
import ssl
from SPARQLWrapper import SPARQLWrapper, JSON
from config.data_config import *
from generate_recipe_2qa import convert_to_standard_unit
def parse_s_expression(s_expr):
    if s_expr.count(',') == 7:
        recipe_name_match = re.search(r"R \[ ingredient , uses \] \) \[ (.*?) \]", s_expr)
        ingredient_name_match = re.search(r"JOIN \( \[ ingredient , name \] \[ (.*?) \]", s_expr)
        if recipe_name_match and ingredient_name_match:
            recipe_name = recipe_name_match.group(1)
            ingredient_name = ingredient_name_match.group(1)
            ingredient_name = ingredient_name.replace(" ", "%20")
            return recipe_name, ingredient_name
        else:
            return None, None
    elif s_expr.count(',') == 15:
        recipe_name_pattern = r"R \[ ingredient , uses \] \) \[ (.*?) \]"
        ingredient_name_pattern = r"JOIN \( \[ ingredient , name \] \[ (.*?) \]"
        recipe_names = re.findall(recipe_name_pattern, s_expr)
        ingredient_names = re.findall(ingredient_name_pattern, s_expr)
        if recipe_names and ingredient_names:
            ingredient_names[0] = ingredient_names[0].replace(" ", "%20")
            return recipe_names[0],recipe_names[2], ingredient_names[0]
        else:
            return None, None, None
        

def generate_sparql_query_sim(recipe_name, ingredient_name):
    # 构建SPARQL查询
    sparql_query = f"""
SELECT ?quantity ?unit
WHERE {{
  ?recipe_uri rdfs:label "{recipe_name}" .
  ?recipe_uri <http://idea.rpi.edu/heals/kb/uses> ?ingredient .
  ?ingredient <http://idea.rpi.edu/heals/kb/ing_name> <http://idea.rpi.edu/heals/kb/ingredientname/{ingredient_name}> .
  ?ingredient <http://idea.rpi.edu/heals/kb/ing_quantity> ?quantity .
  ?ingredient <http://idea.rpi.edu/heals/kb/ing_unit> ?unit .
}}
"""
    return sparql_query
def generate_sparql_query_com(recipe_name1, recipe_name2,ingredient_name):
    # 构建SPARQL查询
    sparql_query = f"""
SELECT ?quantity1 ?unit1 ?quantity2 ?unit2
WHERE {{
  ?recipe_uri1 rdfs:label "{recipe_name1}" .
  ?recipe_uri2 rdfs:label "{recipe_name2}" .
  ?recipe_uri1 <http://idea.rpi.edu/heals/kb/uses> ?ingredient1 .
  ?recipe_uri2 <http://idea.rpi.edu/heals/kb/uses> ?ingredient2 .
  ?ingredient1 <http://idea.rpi.edu/heals/kb/ing_name> <http://idea.rpi.edu/heals/kb/ingredientname/{ingredient_name}> .
  ?ingredient2 <http://idea.rpi.edu/heals/kb/ing_name> <http://idea.rpi.edu/heals/kb/ingredientname/{ingredient_name}> .
  ?ingredient1 <http://idea.rpi.edu/heals/kb/ing_quantity> ?quantity1 .
  ?ingredient1 <http://idea.rpi.edu/heals/kb/ing_unit> ?unit1 .
  ?ingredient2 <http://idea.rpi.edu/heals/kb/ing_quantity> ?quantity2 .
  ?ingredient2 <http://idea.rpi.edu/heals/kb/ing_unit> ?unit2 .
}}
"""
    return sparql_query


def main(s_expr):
    if s_expr.count(',')  == 7:
        recipe_name, ingredient_name = parse_s_expression(s_expr)
        if recipe_name and ingredient_name:
            sparql_query = generate_sparql_query_sim(recipe_name, ingredient_name)
    elif s_expr.count(',') == 15:
        recipe_name1, recipe_name2 ,ingredient_name = parse_s_expression(s_expr)
        if recipe_name1 and recipe_name2 and ingredient_name:
            sparql_query = generate_sparql_query_com(recipe_name1, recipe_name2, ingredient_name)
    else:
        sparql_query = None
    return sparql_query
json_data = "/root/deep/ChatKBQA/Reading/Baichuan2-7b/foodkg/evaluation_beam/beam_test_top_k_predictions.json"
answer_list = []
with open(json_data, 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('qas_dir/test_qas.json', 'r', encoding='utf-8') as f:
    label = json.load(f)
for index, qas in enumerate(data):
    s_expr = qas['predictions'][0]
    sparql_query = main(s_expr)
    ssl._create_default_https_context = ssl._create_unverified_context
    sparql = SPARQLWrapper(USE_ENDPOINT_URL)
    if sparql_query is None:
        answer_list.append(None)
    else:
        try:
            sparql.setQuery(sparql_query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            if s_expr.count(',') == 7:
                answers = [{
                'quantity': x['quantity']['value'],
                'unit': x['unit']['value']
                } for x in results['results']['bindings']]
                if len(answers)>0:
                    answer_list.append(answers[0]['quantity']+" "+answers[0]['unit'])
                else:
                    answer_list.append(None)
            elif s_expr.count(',') == 15:
                answers = [{
                'quantity1': x['quantity1']['value'],
                'unit1': x['unit1']['value'],
                'quantity2': x['quantity2']['value'],
                'unit2': x['unit2']['value']
                } for x in results['results']['bindings']]
                if len(answers)>0:
                    standard_quantity1 = convert_to_standard_unit(answers[0]['quantity1'],answers[0]['unit1'])
                    standard_quantity2 = convert_to_standard_unit(answers[0]['quantity2'],answers[0]['unit2'])
                    if standard_quantity1 and standard_quantity2:
                        if label[index]['is_more']:
                            if standard_quantity1>standard_quantity2:
                                answer_list.append(label[index]['entities'][1][0])
                            else:
                                answer_list.append(label[index]['entities'][2][0])
                        else:
                            if standard_quantity1<standard_quantity2:
                                answer_list.append(label[index]['entities'][1][0])
                            else:
                                answer_list.append(label[index]['entities'][2][0])
                    else:
                        answer_list.append(None)
                else:
                    answer_list.append(None)
        except Exception as e:
            print(e)
            answer_list.append(None)
with open('qas_dir/predict_qas.json', 'w', encoding='utf-8') as f:
    json.dump(answer_list, f, ensure_ascii=False, indent=4)

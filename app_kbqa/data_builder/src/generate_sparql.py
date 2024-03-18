import json

def add_sparql_queries_to_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for qas in data:
        if qas['qType'] == 'simple':
            recipe_uri = qas['uri'][0][0]
            ingredient_name_uri = qas['uri'][1][0]
            sparql_query = f"""SELECT ?quantity ?unit\\n
WHERE {{\\n
  <{recipe_uri}> <http://idea.rpi.edu/heals/kb/uses> ?ingredient .\\n
  ?ingredient <http://idea.rpi.edu/heals/kb/ing_name> <{ingredient_name_uri}> .\\n
  ?ingredient <http://idea.rpi.edu/heals/kb/ing_quantity> ?quantity .\\n
  ?ingredient <http://idea.rpi.edu/heals/kb/ing_unit> ?unit .  \\n
}}"""
            qas['sparql'] = sparql_query
        elif qas['qType'] == 'comparison':
            recipe1_uri = qas['uri'][1][0]
            recipe2_uri = qas['uri'][2][0]
            ingredient_name_uri = qas['uri'][0][0]
            sparql_query = f"""SELECT ?quantity1 ?unit1 ?quantity2 ?unit2\\n
WHERE {{\\n
  <{recipe1_uri}> <http://idea.rpi.edu/heals/kb/uses> ?ingredient1 .\\n
  <{recipe2_uri}> <http://idea.rpi.edu/heals/kb/uses> ?ingredient2 .\\n
  ?ingredient1 <http://idea.rpi.edu/heals/kb/ing_name> <{ingredient_name_uri}> .\\n
  ?ingredient2 <http://idea.rpi.edu/heals/kb/ing_name> <{ingredient_name_uri}> .\\n
  ?ingredient1 <http://idea.rpi.edu/heals/kb/ing_quantity> ?quantity1 .\\n
  ?ingredient1 <http://idea.rpi.edu/heals/kb/ing_unit> ?unit1 .  \\n
  ?ingredient2 <http://idea.rpi.edu/heals/kb/ing_quantity> ?quantity2 .\\n
  ?ingredient2 <http://idea.rpi.edu/heals/kb/ing_unit> ?unit2 .  \\n
}}"""
            qas['sparql'] = sparql_query
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 调用函数为每个 JSON 文件添加 SparQL 查询
add_sparql_queries_to_json('qas_dir/train_qas.json')
add_sparql_queries_to_json('qas_dir/test_qas.json')

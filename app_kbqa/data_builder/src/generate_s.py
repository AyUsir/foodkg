import json

def add_s_to_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for qas in data:
        if qas['qType'] == 'simple':
            recipe = qas['entities'][0][0]
            ingredient_name = qas['entities'][1][0]
            s1 = f"""( JOIN ( R [ ingredient , quantity ] ) ( AND ( JOIN ( R [ ingredient , uses ] ) [ {recipe} ] ) ( JOIN ( [ ingredient , name ] [ {ingredient_name} ] ) ) ) )"""
            s2 = f"""( JOIN ( R [ ingredient , unit ] ) ( AND ( JOIN ( R [ ingredient , uses ] ) [ {recipe} ] ) ( JOIN ( [ ingredient , name ] [ {ingredient_name} ] ) ) ) )"""
            qas['s_quantity'] = s1
            qas['s_unit'] = s2
        elif qas['qType'] == 'comparison':
            recipe1 = qas['entities'][1][0]
            recipe2 = qas['entities'][2][0]
            ingredient_name = qas['entities'][0][0]
            s11 = f"""( JOIN ( R [ ingredient , quantity ] ) ( AND ( JOIN ( R [ ingredient , uses ] ) [ {recipe1} ] ) ( JOIN ( [ ingredient , name ] [ {ingredient_name} ] ) ) ) )"""
            s12 = f"""( JOIN ( R [ ingredient , unit ] ) ( AND ( JOIN ( R [ ingredient , uses ] ) [ {recipe1} ] ) ( JOIN ( [ ingredient , name ] [ {ingredient_name} ] ) ) ) )"""
            s21 = f"""( JOIN ( R [ ingredient , quantity ] ) ( AND ( JOIN ( R [ ingredient , uses ] ) [ {recipe2} ] ) ( JOIN ( [ ingredient , name ] [ {ingredient_name} ] ) ) ) )"""
            s22 = f"""( JOIN ( R [ ingredient , unit ] ) ( AND ( JOIN ( R [ ingredient , uses ] ) [ {recipe2} ] ) ( JOIN ( [ ingredient , name ] [ {ingredient_name} ] ) ) ) )"""
            qas['s_quantity1'] = s11
            qas['s_unit1'] = s12
            qas['s_quantity2'] = s21
            qas['s_unit2'] = s22
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 调用函数为每个 JSON 文件添加 S表达式
add_s_to_json('qas_dir/train_qas.json')
add_s_to_json('qas_dir/test_qas.json')

import json

def llm_to_json(json_file,output):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    result = []
    for qas in data:
        llm = {}
        llm['instruction'] = "Generate a Logical Form query that retrieves the information corresponding to the given question. \n"
        llm['input'] = f"Question: {{{qas['qText']}}} "
        llm['history'] = []
        if qas['qType'] == 'simple':
            llm['output'] = f"{{{qas['s_quantity']}}}, {{{qas['s_unit']}}}"
        elif qas['qType'] == 'comparison':
            llm['output'] = f"{{{qas['s_quantity1']}}}, {{{qas['s_unit1']}}}, {{{qas['s_quantity2']}}}, {{{qas['s_unit2']}}}"
        result.append(llm)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


llm_to_json('qas_dir/train_qas.json','qas_dir/train_llm.json')
llm_to_json('qas_dir/test_qas.json','qas_dir/test_llm.json')

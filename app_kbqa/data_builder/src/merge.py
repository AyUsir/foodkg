import json

def merge_to_json(json_file1,json_file2,output):
    with open(json_file1, 'r', encoding='utf-8') as f:
        data1 = json.load(f)
    with open(json_file2, 'r', encoding='utf-8') as f:
        data2 = json.load(f)
    result = data1+data2
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


merge_to_json('qas_dir/train_llm_and.json','qas_dir/train_llm.json','qas_dir/final_llm.json')

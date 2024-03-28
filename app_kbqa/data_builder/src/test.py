import json
with open('qas_dir/test_qas.json', 'r', encoding='utf-8') as f:
    label = json.load(f)
with open('qas_dir/predict_qas.json', 'r', encoding='utf-8') as f:
    predict = json.load(f)
total = 0
correct = 0
predict_none = 0
answers_none = 0
for index, qas in enumerate(predict):
    if qas == label[index]['answers'][0]:
        correct = correct + 1
    if qas == None:
        predict_none = predict_none + 1
    total = total + 1
print(f"total {total} questions")
print(f"accuracy {100*correct/total}%")
print(f"predict none  {predict_none}")
print(f"correct  {correct}")
print(f"wrong predict {total - correct - predict_none}")
        
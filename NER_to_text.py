import json

from sources.banchmark_conver.NER import tcmner
def readrawdata():
    list=tcmner.getrawdata()
    # with open(file_path,"r",encoding="utf-8") as f:
    #     rawdata=f.readlines()
    #     print(rawdata)
    return list
    pass
##1.转化为连续序列，进行预训练。
#txt-->list
#读取txt文件数据转化为list
def pretraintext(isposition):
    result = []
    if isposition:
        for item in readrawdata():
            #id = item["id"]
            text = item["text"]
            annotations = item['annotations']
            pretext = f"可以从文本:<{text}>中，抽取出以下实体："
            for annotation in annotations:
                label = annotation["label"]
                start_offset = annotation["start_offset"]
                end_offset = annotation["end_offset"]
                entity = annotation["entity"]
                pretext = pretext + label + "-" + entity + f"。实体”{entity}“在原始文本的位置是{start_offset}-{end_offset}。"
            #print(pretext)
            text_dict={"text":pretext}
            result.append(text_dict)
    else:
        for item in readrawdata():
            #id = item["id"]
            text = item["text"]
            annotations = item['annotations']
            pretext = f"可以从文本:<{text}>中，抽取出以下实体："
            for annotation in annotations:
                label = annotation["label"]
                entity = annotation["entity"]
                pretext = pretext + label + "-" + entity + f"。"
            #print(pretext)
            text_dict={"text":pretext}
            result.append(text_dict)
    return result
##2.转化为指令微调形式（问答对），进行微调。
def finetuningtext(isposition):
    result = []
    if isposition:
        for item in readrawdata():
            #id = item["id"]
            text = item["text"]
            annotations = item['annotations']
            pretext = f"现在你是中医药领域专家，请从文本:<{text}>中，抽取出中医药相关实体。"
            answertext=f"从中抽取出如下实体（包括实体在原始文本中的位置信息）:"
            for annotation in annotations:
                label = annotation["label"]
                start_offset = annotation["start_offset"]
                end_offset = annotation["end_offset"]
                entity = annotation["entity"]
                answertext = answertext + label + "-" + entity + f"。实体”{entity}“在原始文本的位置是{start_offset}-{end_offset}。"
            #print(pretext)
            text_dict={"question":pretext,"answer":answertext}
            result.append(text_dict)
    else:
        for item in readrawdata():
            #id = item["id"]
            text = item["text"]
            annotations = item['annotations']
            pretext = f"现在你是中医药领域专家，请从文本:<{text}>中，抽取出中医药相关实体。"
            answertext = f"从中抽取出如下相关实体如下:"
            for annotation in annotations:
                label = annotation["label"]
                entity = annotation["entity"]
                pretext = pretext + label + "-" + entity + f"。"
            text_dict={"question":pretext,"answer":answertext}
            result.append(text_dict)
    return result
    pass
def onlytext():
    result = []
    for item in readrawdata():
        # id = item["id"]
        text = item["text"]
        text_dict = {"text": text}
        result.append(text_dict)
    return result

def save(dict,path):
    print("save to ",path)
    json_str = json.dumps(dict,ensure_ascii=False)
    with open(path,"a+",encoding='utf-8') as f:
        f.write(str(json_str))
        f.write('\n')
if __name__=="__main__":
    #file_path="C:\\Users\\zhangheyi\\Desktop\\dataprocess\\DATA\\banchmark\\中药说明书实体识别\\中药说明书实体识别\\中医实体.txt"
    #readrawdata(file_path)
    # isposition=False
    # texts=pretraintext(isposition)
    # print(texts)
    # for text in texts:
    #     save(text,f"pretrain{isposition}.json")
    # texts=finetuningtext(isposition)
    # print(texts)
    # for text in texts:
    #     save(text, f"finetuning{isposition}.json")
    texts=onlytext()
    print(texts)
    for text in texts:
        save(text, f"onlytext.json")

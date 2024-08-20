import json
def onlytext(rawdata):
    texts=[]
    for item in rawdata:
        text={"text":item["text"]}
        texts.append(text)
    return texts
    pass
def pretext(type,rawdata):
    if type==1:
        result=[]
        for item in rawdata:
            text = item["text"]
            annotations = item['annotations']
            pretext = f"可以从文本:<{text}>中，生成以下问答对："
            id=0
            for annotation in annotations:
                id+=1
                question = annotation["Q"]
                answer = annotation["A"]
                pretext = pretext + f"{id}.问题:"+question + "答案是：" + answer
            # print(pretext)
            text_dict = {"text": pretext}
            result.append(text_dict)
        return result
    elif type==2:
        result=[]
        for item in rawdata:
            text = item["text"]
            annotations = item['annotations']
            for annotation in annotations:
                question = annotation["Q"]
                answer = annotation["A"]
                pretext = f"请回答问题:{question} \n根据<{text}>中的内容，我给出的答案是：{answer}"
                text_dict = {"text": pretext}
                result.append(text_dict)
        return result
    elif type==3:
        result=[]
        for item in rawdata:
            text = item["text"]
            annotations = item['annotations']
            for annotation in annotations:
                question = annotation["Q"]
                answer = annotation["A"]
                pretext = f"问题:{question} 的答案是：{answer}"
                text_dict = {"text": pretext}
                result.append(text_dict)
        return result
    pass
def fintext(type,rawdata):
    if type == 1:
        result = []
        for item in rawdata:
            text = item["text"]
            annotations = item['annotations']
            question = f"请根据文本:<{text}>，生成一些问答对。"
            answer="可以从中生成如下问答对："
            id = 0
            for annotation in annotations:
                id += 1
                Q = annotation["Q"]
                A = annotation["A"]
                answer = answer + f"{id}.问题:" + Q + "答案是：" + A
                # print(pretext)
            text_dict = {"question": question,"answer":answer}
            result.append(text_dict)
        return result
    elif type == 2:
        result = []
        for item in rawdata:
            text = item["text"]
            annotations = item['annotations']
            for annotation in annotations:
                Q = annotation["Q"]
                A = annotation["A"]
                question = f"请回答问题:{Q} "
                answer=f"根据<{text}>，答案是：{A}"
                text_dict = {"question": question,"answer":answer}
                result.append(text_dict)
        return result
    elif type == 3:
        result = []
        for item in rawdata:
            annotations = item['annotations']
            for annotation in annotations:
                question = annotation["Q"]
                answer = annotation["A"]
                text_dict = {"question": question,"answer":answer}
                result.append(text_dict)
        return result
    pass
def readjson(file):
    with open(file,"r",encoding="utf-8") as f:
        jsondata=json.load(f)
        print(jsondata)
    return jsondata
    pass

def save(dict,path):
    print("save to ",path)
    json_str = json.dumps(dict,ensure_ascii=False)
    with open(path,"a+",encoding='utf-8') as f:
        f.write(str(json_str))
        f.write('\n')
if __name__=="__main__":
    filepath="C:\\Users\zhangheyi\Desktop\dataprocess\DATA\\banchmark\中医问答对生成\\train.json"
    rawdata=readjson(filepath)
    texts=onlytext(rawdata)
    for text in texts:
        save(text, f"onlytext.json")
    for type in range(1,4):
        print(type)
        texts = pretext(type,rawdata)
        for text in texts:
            save(text, f"pretext{type}.json")
        texts = fintext(type,rawdata)
        for text in texts:
            save(text, f"fintext{type}.json")
    pass
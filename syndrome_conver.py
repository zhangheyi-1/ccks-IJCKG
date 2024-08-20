#根据患者症状描述，判断出主要症状，结合观察，判断出是什么证候，并根据证候开出药方
import json


def readrawdata():
    train="C:\\Users\\zhangheyi\\Desktop\\dataprocess\\DATA\\banchmark\\中医症状判别\\train.json"
    syndrome_knowledge = "C:\\Users\\zhangheyi\\Desktop\\dataprocess\\DATA\\banchmark\\中医症状判别\\syndrome_knowledge.json"
    with open(train,"r",encoding="utf-8") as f:
        data = f.readlines()
        train_data=[]
        #print(data)
        for item in data:
            train_data_item=json.loads(item)
            train_data.append(train_data_item)
        print(train_data)
    f.close()
    with open(syndrome_knowledge,"r",encoding="utf-8") as f2:
        data = f2.readlines()
        syndrome_knowledge_data = []
        for item in data:
            syndrome_knowledge_item = json.loads(item)
            syndrome_knowledge_data.append(syndrome_knowledge_item)
        #print(syndrome_knowledge)
    return [train_data,syndrome_knowledge_data]
def fulltext(data):
    texts = []
    for item in data:
        lcd_name = item["lcd_name"]
        syndrome = item["syndrome"]
        chief_complaint = item["chief_complaint"]
        description = item["description"]
        detection = item["detection"]
        text = f"{description}患者主要症状为{chief_complaint}。患者{detection}。判断患者为{lcd_name}，属{syndrome}。"
        texts.append({"text": text})
    return texts
    pass
def syndrometext(data):
    texts = []
    for item in data:
        syn_name = item["Name"]
        syn_def = item["Definition"]
        syn_Typ = item["Typical_performance"]
        syn_iss = item["Common_isease"]
        text = f"{syn_name}{syn_def}典型症状有{syn_Typ}常见于{syn_iss}"
        texts.append({"text":text})
    return texts
    pass
def finsyntext(data):
    findata=[]
    for item in data:
        syn_name=item["Name"]
        syn_def = item["Definition"]
        syn_Typ = item["Typical_performance"]
        syn_iss = item["Common_isease"]
        questions=[f"{syn_name}是什么？",f"{syn_name}常见于什么疾病？一般是什么病？",f"{syn_name}典型症状是什么？",f"{syn_name}是什么？有什么典型症状？常见于什么疾病？"]
        answers=[f"{syn_name}{syn_def}",f"{syn_iss}",f"{syn_name}的典型症状有{syn_Typ}",f"{syn_name}{syn_def}典型症状有{syn_Typ}常见于{syn_iss}"]

        for i in range(0,4):
            #print(i)
            fine_item={"question":questions[i],"answer":answers[i]}
            print(fine_item)
            findata.append(fine_item)
    return findata
    pass
def finfulltext(data):
    texts = []
    for item in data:
        lcd_name = item["lcd_name"]
        syndrome = item["syndrome"]
        chief_complaint = item["chief_complaint"]
        description = item["description"]
        detection = item["detection"]
        question = f"根据患者的病情描述：<{description}>和观测情况：<患者{detection}>判断患者的主要症状是什么？"
        answer=f"患者的主要症状为{chief_complaint}，判断患者为{lcd_name}，属{syndrome}。"
        texts.append({"question": question,"answer":answer})
    return texts
    pass
def save(dict,path):
    print("save to ",path)
    json_str = json.dumps(dict,ensure_ascii=False)
    with open(path,"a+",encoding='utf-8') as f:
        f.write(str(json_str))
        f.write('\n')
if __name__=="__main__":
    data=readrawdata()
    #print(data[0])
    #print(data[1])
    # finsyndata=finsyntext(data[1])
    # for text in finsyndata:
    #     save(text, f"finsyndata.json")
    # texts = syndrometext(data[1])
    # for text in texts:
    #     save(text, f"presyndata.json")
    texts = fulltext(data[0])
    for text in texts:
        save(text, f"prefulltext.json")
    # texts = finfulltext(data[0])
    # for text in texts:
    #     save(text, f"finfulltext.json")

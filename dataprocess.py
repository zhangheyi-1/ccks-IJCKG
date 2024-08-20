#coding=utf-8
##1.需要将多个txt数据拼接到一起，注意分隔与去除目录，四库全书，中医药书籍等
#古文数据/医药书籍：中医药。
#madical_book需要提取出text。
##2.将翻译中的原文src与译文对应起来拼接到一起，有些是再一个json文件里，有些是分别存在了两个文件里，原文和译文按行一一对应
#古今文翻译
#中英翻译
##3.json文件问答可以直接将问题与答案合并到一段话，
#问答对话数据
##4.title和content直接拼接到一起，组成一段话
#通用知识：wudao
##6.instruct 与input ouptput拼接到一起
##
##5.注意不同的段落要添加上分割标记

import json
import os
import re
import string
from tqdm import tqdm

import time

line = True##是否保留换行’\n‘
##可替换字符字典
replacedict = {'': '翛',
               '': '棨',
               '': '雱',
               '': '慓',
               '': '祐',
               'Ι': '禼',
               '': '蠢',
               'к': '韡',
               '': '抃',
               '': '悰',
               '': '鄘',
               '': '濊',
               '': '勚',
               "":"垕",
               "":"駸",
               "*":"",
               }
##判断字符是否是正常汉字
def is_chinese(uchar,encoding='utf-8'):
    # 1.GBK(GB2312 / GB18030)
    # x00 - xff GBK双字节编码范围
    # x20 - x7f ASCII
    # xa1 - xff 中文
    # x80 - xff 中文
    # 2.UTF - 8(Unicode)
    # u4e00 - u9fa5(中文)
    # x3130 - x318F(韩文)
    # xAC00 - xD7A3(韩文)
    # u0800 - u4e00(日文)
    ##主流的匹配字符有两种 [\u4e00-\u9fa5]和[\u2E80-\u9FFF]，后者范围更广，包括了日韩地区的汉字
    if encoding=='utf-8':
        if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        #if uchar >= u'\u0080' and uchar <= u'\u07FF':
            return True
        else:
            return False
    elif encoding=='GBK':
        if uchar >= '\x80' and uchar <= '\xff':
        #if uchar >= u'\u0080' and uchar <= u'\u07FF':
            return True
        else:
            return False
##判断字符是否是正常英文标点
def is_punctuation(char):
    if char in string.punctuation:
        return True
    else:
        return False
##判断是否是正常中文标点
def is_chiesepunctuation(char):
    if char in ['[',']','【','】','。','，','/',',','.','？','、','！','；','：','“','’','《','》']:
        return True
    else:
        return False
##判断是否需要替换
def is_needreplace(char):
    if char in replacedict.keys():
        return True
    else:
        return False
##当char需要替换时，进行替换
def replacechar(char):
    return replacedict[char]
def getallfilesnum(path):
    files_num={}
    for dirpath, dirnames, filenames in os.walk(path):
        #print(dirpath,dirnames,filenames)
        key=dirpath
        num=0
        files_num[key]=num
        for filename in filenames:
            files_num[dirpath]+=1
    return files_num

def check(text):
    print("人工检查有无问题")
    print(text)
    #time.sleep(10)
def guwenbookprocess(type):
    results=[]
    result={}
    if type == "daizhige":
        ##daizhige是txt文档
        guwenpath=r'C:\Users\zhangheyi\Desktop\dataprocess\new_data\pretrain\rawdata\BOOK\中医\中医药古籍'
        files = getallfiles(guwenpath)
        num=0
        for file_path in files:
            num+=1
            print(num)
            print(file_path)
            if file_path=='test':
                with (open(file_path,"r",encoding='UTF-8') as f) :
                    #print(f.name)
                    res = f.read()
                    res=re.sub(r'[○■●■▆Ψ{}]',"",res)
                    res=res.replace("","翛")
                    res=res.replace("", "")
                    res=res.replace("","棨")
                    res=res.replace("", "鄘")
                    res=res.replace("", "濊")
                    res=res.replace("", "勚")
                    res=res.replace("", "")
                    res=res.replace("", "")
                    res=res.replace("", '悰')
                    res=res.replace("", '抃')
                    res=res.replace("к", '韡')
                    res=res.replace("", '蠢')
                    res=res.replace("Ι", '禼')
                    res=res.replace("",'祐')
                    res=res.replace('',"慓")
                    res=res.replace('',"雱")
                    res=res.replace("oe","")
                    res=res.replace("[A085]", "")
                    res=res.replace("&#8226;","·")
                    res=res.replace("","垕")
                    res = res.replace("", "駸")
                    res=res.replace('　　',',')
                    res = res.replace('\n', '。')
                    res = res.replace('。。', '。')
                    res = res.replace('。。', '。')
                    res = res.replace('。,', ';')
                    res = res.replace(';。', '。')
                    res=re.sub(r'[(。;)]',"",res)
                    result={"source":res,"target":''}
                    #print(result)
                    results.append(result)
            else:
                with (open(file_path,"r",encoding='gbk') as f) :
                    res = f.read()
                    text=''
                    ##去除文章中的乱码，特殊字符。
                    for char in res:
                        if char=='\n':
                            if line:
                                text+=char
                        if is_chinese(char):
                            text+=char
                        elif is_punctuation(char):
                            text+=char
                        elif is_chiesepunctuation(char):
                            text += char
                        elif is_needreplace(char):
                            text+=replacechar(char)
                        else:
                            pass
                    ##全角空格表示分割，改为’ ‘
                    ##print(hex(ord('　'))) ord获取全角空格对应十进制数字，hex将其转化为16进制数，从而使用unicode编码表示
                    text = re.sub(r'[\u3000]+', ",", text)
                    text=text.replace('\n,','\n')
                    text = text.replace('\n“', '\n')
                    ##大于等于2个\n增加分割标记
                    text = re.sub(r'\n[\u3000]+', "\n", text)
                    ##到此处text为去除特殊字符后的，中文序列
                    texts=text.split("\n\n")
                    content = ''
                    for text in texts:
                        if text=="\n":
                            pass
                        else:
                            content+=text+'\n'
                    ##去除连续非文本字符
                    content=re.sub(r'[？()<=>|\-][？()<=>|\-]+', "", content)
                    ##检查是否包含标题,\n，保留连续内容
                    content = content.replace('\n【', '\n')  ##存在某些标题以】为标识
                    content = content.replace('】\n', '：')##去除标题标识修改为:
                    content = content.replace('】', '：')
                    content = content.replace('【', '')
                    content=content.replace('\n','。')
                    content = content.replace('。。', '。\n') ##存在有些句子以\n表示一句话的结束
                    contents=content.split('\n')
                    content_new=''
                    for i in contents:
                        if len(i)<5:
                            content_new+='\n'
                        elif len(i)>15:
                            content_new+=i
                        elif re.search(r'卷[一二三四五六七八九十]+',i):
                            content_new+='\n'
                        else:
                            content+=i
                    ##存在某些标题以】为标识
                    content_new=content_new.replace('’','')##去除不必要的‘符号
                    content_news=content_new.split('\n')
                    for i in content_news:
                        if len(i)>10:
                            i=i.replace('?。','?')
                            result={"text":i}
                        else:
                            pass
                        #print(result)
                        save(result, 'tcmtb.json')
                        results.append(result)##清洗好后的数据加入结果列表
        #print(results)
        return results
    if type == "siku":
        guwenpath = 'C:\\Users\\zhangheyi\\Desktop\\dataprocess\\DATA\\古文数据\\四库全书'
        files = getallfiles(guwenpath)
        num = 0
        for file_path in files:
            num += 1
            print(num)
            with (open(file_path, "r", encoding='UTF-8') as f):
                res = f.read()
                text = ''
                ##去除文章中的乱码，特殊字符。
                for char in res:
                    if char == '\n':
                        if line:
                            text += char
                    if is_chinese(char):
                        text += char
                    elif is_punctuation(char):
                        text += char
                    elif is_chiesepunctuation(char):
                        text += char
                    elif is_needreplace(char):
                        text += replacechar(char)
                    else:
                        pass
    if type == "li":
        file_path = 'C:\\Users\\zhangheyi\\Desktop\\dataprocess\\DATA\\古文数据\\daizhigev20-master\\daizhigev20-master\\集藏\\四库别集\\临川集.txt'
        with (open(file_path, "r", encoding='GBK') as f):
            res = f.read()
            text = ''
            ##去除文章中的乱码，特殊字符。
            for char in res:
                if char == '\n':
                    if line:
                        text += char
                if is_chinese(char):
                    text += char
                elif is_punctuation(char):
                    text += char
                elif is_chiesepunctuation(char):
                    text += char
                elif is_needreplace(char):
                    text += replacechar(char)
                else:
                    pass
            ##全角空格表示分割，改为’ ‘
            ##print(hex(ord('　'))) ord获取全角空格对应十进制数字，hex将其转化为16进制数，从而使用unicode编码表示
            text = re.sub(r'[\u3000]+', ",", text)
            text = text.replace('\n,', '\n')
            text = text.replace('\n“', '\n')
            ##大于等于2个\n增加分割标记
            text = re.sub(r'\n[\u3000]+', "\n", text)
            text = text.replace('\n【', '\n')  ##存在某些标题以】为标识
            text = text.replace('】\n', '：')  ##去除标题标识修改为:
            ##到此处text为去除特殊字符后的，中文序列
            content=text
            ##去除连续非文本字符
            content = re.sub(r'[？()<=>|\-][？()<=>|\-]+', "", content)
            ##检查是否包含标题,去除标题,\n，保留连续内容
            contents = content.split('\n')
            content_new = ''
            for i in contents:
                if len(i) < 5:
                    content_new += '\n'
                elif len(i) > 15:
                    content_new += i
                elif re.search(r'卷[一二三四五六七八九十]+', i):
                    content_new += '\n'
                else:
                    content += i

            content_news = content_new.split('\n')
            for i in content_news:
                if len(i) > 100:
                    i = i.replace('?。', '?')
                    result = {"source": i, "target": ''}
                else:
                    pass
                print(result)
                #save(result, 'daizhige.json')
                results.append(result)
        pass
    if type == "yizang":
        ##daizhige是txt文档
        guwenpath = r'C:\Users\zhangheyi\Desktop\dataprocess\new_data\pretrain\rawdata\BOOK\中医\医藏'
        files = getallfiles(guwenpath)
        num = 0
        for file_path in tqdm(files):
            num += 1
            #print(num)
            #print(file_path)
            with (open(file_path, "r", encoding='utf-8') as f):
                res = f.read()
                text = ''
                ##去除文章中的乱码，特殊字符。
                for char in res:
                    if char == '\n':
                        if line:
                            text += char
                    if is_chinese(char):
                        text += char
                    elif is_punctuation(char):
                        text += char
                    elif is_chiesepunctuation(char):
                        text += char
                    elif is_needreplace(char):
                        text += replacechar(char)
                    else:
                        pass
                ##全角空格表示分割，改为’ ‘
                ##print(hex(ord('　'))) ord获取全角空格对应十进制数字，hex将其转化为16进制数，从而使用unicode编码表示
                text = re.sub(r'[\u3000]+', ",", text)
                text = text.replace('\n,', '\n')
                text = text.replace('\n“', '\n')
                ##大于等于2个\n增加分割标记
                text = re.sub(r'\n[\u3000]+', "\n", text)
                ##到此处text为去除特殊字符后的，中文序列
                texts = text.split("\n")
                content = ''
                for text in texts:
                    if text == "\n":
                        pass
                    else:
                        content += text + '\n'
                ##去除连续非文本字符
                content = re.sub(r'[？()<=>|\-][？()<=>|\-]+', "", content)
                ##检查是否包含标题,\n，保留连续内容
                content = content.replace('\n【', '\n')  ##存在某些标题以】为标识
                content = content.replace('】\n', '：')  ##去除标题标识修改为:
                content = content.replace('】', '：')
                content = content.replace('【', '')
                # content = content.replace('\n', '。')
                content = content.replace('。。', '。\n')  ##存在有些句子以\n表示一句话的结束
                contents = content.split('\n')
                content_new = ''
                for i in contents:
                    if len(i) <=5:
                        content_new += '\n\n'+i
                    elif len(i) > 5:
                        content_new += i
                    elif re.search(r'卷[一二三四五六七八九十]+', i):
                        content_new += '\n\n'
                    else:
                        content += i
                ##存在某些标题以】为标识
                content_new = content_new.replace('’', '')  ##去除不必要的‘符号
                #print(content_new)
                content_news = content_new.split('\n\n\n')
                for i in content_news:
                    if len(i) > 10:
                        #print(i)
                        i = i.replace('\n\n', '。')
                        i = i.replace('。。', '。')
                        i = i.replace('。。', '。')
                        i = i.replace('\n', '')
                        result = {"text": i}
                        save(result, 'yizang.json')
                        results.append(result)  ##清洗好后的数据加入结果列表
                    else:
                        pass
                    # print(result)

        # print(results)
        return results

def getallfiles(path):
    ##得到当前目录下的所有文件路径
    ##返回路径list []
    files=[]
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file = os.path.join(dirpath, filename)
            #print(file)
            files.append(file)
    return files

##结果写入json文件
def save(dict,path):
    #print("save to ",path)
    json_str = json.dumps(dict,ensure_ascii=False)
    with open(path,"a+",encoding='utf-8') as f:
        f.write(str(json_str))
        f.write('\n')
def alltegather(allpath):
    files = getallfiles(allpath)
    for file_path in files:
        print(file_path)
        with open(file_path,"r",encoding='UTF-8') as f:
            for json_data in f.readlines():
                j = json.loads(json_data)
                print(type(j))
                print(j)
                item = {"source":j['source'],"target":j['target']}
                save(item,'all.json')
if __name__=='__main__':
    #print('test')
    #allpath=('C:\\Users\\zhangheyi\\Desktop\\dataprocess\\zirui_1all')
    ##print(getallfiles('C:\\Users\\zhangheyi\\Desktop\\dataprocess\\DATA'))
    guwenbookprocess("yizang")##return json{"source":"","target":""}
    #guwenbookprocess("siku")
    #guwenbookprocess("li")
    #guwenbookprocess("monolingual")
    #alltegather(allpath)
    pass

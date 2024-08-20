# Copyright 2023 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

"""
transform wikitext-2, wikitext-103, lambada, openwebtext dataset to mindrecord.
"""
import sys
import argparse
import json
import os
import re
import numpy as np
import string
from tqdm import tqdm
import time

from mindspore.mindrecord import FileWriter

from mindformers.models.llama.llama_tokenizer import LlamaTokenizer

IGNORE_TOKEN_ID = -100


def chunks(lst, n):
    """ yield n sized chunks from list"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def package_file(it, n):
    """ package multiple files"""
    stop = False
    while not stop:
        batch = []
        for _ in range(n):
            try:
                batch.append(next(it))
            except StopIteration:
                stop = True
        if not batch:
            break
        yield batch


def clean_wikitext(string):
    """ cleaning wikitext dataset"""
    # contractions
    string = string.replace("s '", "s'")
    string = re.sub(r"/' [0-9]/", r"/'[0-9]/", string)
    # number separators
    string = string.replace(" @-@ ", "-")
    string = string.replace(" @,@ ", ",")
    string = string.replace(" @.@ ", ".")
    # punctuation
    string = string.replace(" : ", ": ")
    string = string.replace(" ; ", "; ")
    string = string.replace(" . ", ". ")
    string = string.replace(" ! ", "! ")
    string = string.replace(" ? ", "? ")
    string = string.replace(" , ", ", ")
    # double brackets
    string = re.sub(r"\(\s*([^\)]*?)\s*\)", r"(\1)", string)
    string = re.sub(r"\[\s*([^\]]*?)\s*\]", r"[\1]", string)
    string = re.sub(r"{\s*([^}]*?)\s*}", r"{\1}", string)
    string = re.sub(r"\"\s*([^\"]*?)\s*\"", r'"\1"', string)
    string = re.sub(r"'\s*([^']*?)\s*'", r"'\1'", string)
    # miscellaneous
    string = string.replace("= = = =", "====")
    string = string.replace("= = =", "===")
    string = string.replace("= =", "==")
    string = string.replace(" " + chr(176) + " ", chr(176))
    string = string.replace(" \n", "\n")
    string = string.replace("\n ", "\n")
    string = string.replace(" N ", " 1 ")
    string = string.replace(" 's", "'s")
    return string


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
               "": "垕",
               "": "駸",
               "*": "",
               }


##判断字符是否是正常汉字
def is_chinese(uchar, encoding='utf-8'):
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
    if encoding == 'utf-8':
        if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
            # if uchar >= u'\u0080' and uchar <= u'\u07FF':
            return True
        else:
            return False
    elif encoding == 'GBK':
        if uchar >= '\x80' and uchar <= '\xff':
            # if uchar >= u'\u0080' and uchar <= u'\u07FF':
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
    if char in ['[', ']', '【', '】', '。', '，', '/', ',', '.', '？', '、', '！', '；', '：', '“', '’', '《', '》']:
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


def is_number(char):
    return char.isalnum()


def clean_alltext(texts):
    # punctuation
    string = texts
    string = string.replace(" : ", ": ")
    string = string.replace(" ; ", "; ")
    string = string.replace(" . ", ". ")
    string = string.replace(" ! ", "! ")
    string = string.replace(" ? ", "? ")
    string = string.replace(" , ", ", ")
    # double brackets
    string = re.sub(r"\(\s*([^\)]*?)\s*\)", r"(\1)", string)
    string = re.sub(r"\[\s*([^\]]*?)\s*\]", r"[\1]", string)
    string = re.sub(r"{\s*([^}]*?)\s*}", r"{\1}", string)
    string = re.sub(r"\"\s*([^\"]*?)\s*\"", r'"\1"', string)
    string = re.sub(r"'\s*([^']*?)\s*'", r"'\1'", string)
    texts = string
    text = ''
    for char in texts:
        if char == '\n':
            text += char
        if is_chinese(char):
            text += char
        elif is_punctuation(char):
            text += char
        elif is_chiesepunctuation(char):
            text += char
        elif is_needreplace(char):
            text += replacechar(char)
        elif is_number(char):
            text += char
        else:
            pass
    return text


def tokenize_wiki(tokenizer, file_path, seq_length, repeat):
    """tokenize wikitext-2/wikitext-103 dataset"""
    content = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for para in clean_wikitext(f.read()).split("\n\n"):
            if para and para.strip().startswith('=') is False:
                print(para)
                content += tokenizer(para)['input_ids']

    content_out = []
    for _ in range(repeat):
        content_out.extend(content)
    content = content_out
    for chunk in chunks(content, seq_length):
        sample = {}
        if len(chunk) == seq_length:
            sample['input_ids'] = np.array(chunk, dtype=np.int32)
            yield sample


def tokenize_baike(tokenizer, file_path, seq_length, repeat):
    f = open(file_path, 'r')
    cnt = 0
    doc_ids = []
    while True:
        line = f.readline()
        if not line:
            break
        line = json.loads(line)
        text = ''
        try:
            text += line['title'] + '：' + line['summary']
        except:
            pass
        for per in line['sections']:
            text += per['title'] + '：' + per['content'] + '。'
        text_id = tokenizer(text)['input_ids']
        if len(text_id) > 5:
            doc_ids += text_id
        cnt += 1
        if cnt % 10000 == 0:
            print(cnt)
    content_out = []
    for _ in range(repeat):
        content_out.extend(doc_ids)
    content = content_out
    for chunk in chunks(content, seq_length):
        sample = {}
        if len(chunk) == seq_length:
            sample['input_ids'] = np.array(chunk, dtype=np.int32)
            yield sample


def tokenize_all(tokenizer, file_path, seq_length, repeat):
    """tokenize wikitext-2/wikitext-103 dataset"""
    """get the file from /run/data/ """

    def getallfiles(path):
        ##得到当前目录下的所有文件路径
        ##返回路径list []
        files = []
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file = os.path.join(dirpath, filename)
                # print(file)
                files.append(file)
        return files

    files = getallfiles('/run/data')
    content = []
    print("loading all files: ")
    for file_path in tqdm(files):
        print("loading ", file_path)
        with open(file_path, "r", encoding='UTF-8') as f:
            # num=0
            while True:
                line = f.readline()
                if not line:
                    break
                try:
                    j = json.loads(line)
                    item = {"source": j['source'], "target": j['target']}
                except:
                    pass
                # print('#')
                # print(j)
                if len(item['source']) + len(item['target']) > 10:
                    para = clean_alltext(item['source'] + item["target"])
                    # num+=1
                    # print(num)
                    content += tokenizer(para)['input_ids']
    # with open(file_path, 'r', encoding='utf-8') as f:
    #     for para in clean_wikitext(f.read()).split("\n\n"):
    #         if para and para.strip().startswith('=') is False:
    #             print(para)
    #             content += tokenizer(para)['input_ids']
    content_out = []
    for _ in range(repeat):
        content_out.extend(content)
    content = content_out
    for chunk in chunks(content, seq_length):
        sample = {}
        if len(chunk) == seq_length:
            sample['input_ids'] = np.array(chunk, dtype=np.int32)
            yield sample


def tokenize_all_parallel(tokenizer, file_path, seq_length, repeat):
    content = []
    print("loading files: file_path")
    with open(file_path, "r", encoding='UTF-8') as f:
        # num=0
        while True:
            try:
                line = f.readline()
                if not line:
                    break
                try:
                    j = json.loads(line)
                    item = {"source": j['source'], "target": j['target']}
                except Exception as e:
                    print(e)
                # print('#')
                # print(j)
                if len(item['source']) + len(item['target']) > 10:
                    para = clean_wikitext(item['source'] + item["target"])
                    content += tokenizer(para)['input_ids']
                    # print('tokenizeing')
            except Exception as e:
                print(e)
    content_out = []
    for _ in range(repeat):
        content_out.extend(content)
    content = content_out
    for chunk in chunks(content, seq_length):
        sample = {}
        if len(chunk) == seq_length:
            sample['input_ids'] = np.array(chunk, dtype=np.int32)
            yield sample


if __name__ == '__main__':
    test = False
    ##为指定的json文件，创建转化路径。
    # 设置默认的参数：
    filename = sys.argv[1]
    dir_ = sys.argv[2]
    output_file_name = filename.replace('.json', '.mindrecord')
    input_glob = '/run/data/' + filename
    output_file = '/run/data/' + dir_ + '/' + output_file_name

    if test == True:
        print(input_glob, output_file)
        for i in tqdm(range(10000)):
            print(i)
            time.sleep(1)
    else:
        dataset_type = 'tokenize_all_parallel'
        filename = sys.argv[1]
        dir_ = sys.argv[2]
        output_file_name = filename.replace('.json', '.mindrecord')
        input_glob = '/run/data/' + filename
        output_file = '/run/data/' + dir_ + '/' + output_file_name
        parser = argparse.ArgumentParser()
        parser.add_argument('filename', type=str, default=dataset_type)
        parser.add_argument('dir', type=str, default=dataset_type)
        parser.add_argument('--dataset_type', type=str, default=dataset_type)
        parser.add_argument('--input_glob', type=str, default=input_glob)
        parser.add_argument('--output_file', type=str, default=output_file)
        parser.add_argument('--tokenizer', type=str, default='llama', choices=['llama'])
        parser.add_argument('--model_file', type=str,
                            default='/home/mindformer/mindformers/Data/llama-7b/tokenizer/merged_tokenizer_sp/chinese_llama.model')
        parser.add_argument('--file_partition', type=int, default=1)
        parser.add_argument('--repeat', type=int, default=1)
        parser.add_argument('--seq_length', type=int, default=2048)
        args = parser.parse_args()
        schema = {'input_ids': {"type": "int32", "shape": [-1]}, }
        out_dir, out_file = os.path.split(os.path.abspath(args.output_file))
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        if args.dataset_type == 'wiki':
            schema = {'input_ids': {"type": "int32", "shape": [-1]}, }
        elif args.dataset_type == 'qa':
            schema = {'input_ids': {"type": "int32", "shape": [-1]}, 'labels': {"type": "int32", "shape": [-1]}}
        writer = FileWriter(file_name=args.output_file,
                            shard_num=args.file_partition, overwrite=True)
        writer.add_schema(schema, args.dataset_type)
        writer.open_and_set_header()

        # Start to load tokenizer
        if not os.path.exists(args.model_file):
            raise FileNotFoundError(f"file {args.model_file} do not exists.")

        transforms_count = 0
        word_tokenizer = LlamaTokenizer(vocab_file=args.model_file)
        if hasattr(word_tokenizer, 'add_bos_token'):
            word_tokenizer.add_bos_token = True
        if hasattr(word_tokenizer, 'add_eos_token'):
            word_tokenizer.add_eos_token = True
        if args.dataset_type == 'wiki':
            for x in tokenize_wiki(word_tokenizer, args.input_glob, args.seq_length + 1, args.repeat):
                transforms_count += 1
                writer.write_raw_data([x])
            print("Transformed {} records.".format(transforms_count))
        elif args.dataset_type == 'baike':
            for x in tokenize_baike(word_tokenizer, args.input_glob, args.seq_length + 1, args.repeat):
                transforms_count += 1
                writer.write_raw_data([x])
            print("Transformed {} records.".format(transforms_count))
        elif args.dataset_type == 'tokenize_all_parallel':
            for x in tokenize_all_parallel(word_tokenizer, args.input_glob, args.seq_length + 1, args.repeat):
                transforms_count += 1
                writer.write_raw_data([x])
            print("Transformed {} records.".format(transforms_count))
        else:
            raise ValueError(
                "Not support dataset type: {}".format(args.dataset_type))

        writer.commit()
        out_file = args.output_file
        if args.file_partition > 1:
            out_file += '0'
        print("Transform finished, output files refer: {}".format(out_file))

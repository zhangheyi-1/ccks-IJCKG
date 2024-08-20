"""
fastchat stanford alpaca data convert tools.
"""

import argparse

import json

import pathlib

# Prompt from stanford alpaca's training script

PROMPT_DICT = {
    "prompt_input": (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:"
    ),

    "prompt_no_input": (
        "{instruction}"
    ),

}

def main(args_param):
    data_path = args_param.data_path
    data = []
    with open(args_param.data_path,"r",encoding="utf-8") as f:
        for item in f.readlines():
            dict_item = json.loads(item)
            print(dict_item)
            if "query" in dict_item:
                data_item={"instruction":dict_item["query"],"input": "","output": dict_item["response"]}
                data.append(data_item)
            if "source" in dict_item:
                data_item = {"instruction": dict_item["source"], "input": "", "output": dict_item["target"]}
                data.append(data_item)

    # with data_path.open() as f:
    #     data = json.load(f)
    prompt_input, prompt_no_input = (
        PROMPT_DICT["prompt_input"],
        PROMPT_DICT["prompt_no_input"],
    )

    sources = [
        prompt_input.format_map(example)
        if example.get("input", "") != ""
        else prompt_no_input.format_map(example)
        for example in data
    ]

    targets = [example["output"] for example in data]

    new_data = []

    cnt = 1

    for s, t in zip(sources, targets):
        new_data.append(
            {
                "id": str(cnt),
                "conversations": [
                    {
                        "from": "human",
                        "value": s,
                    },
                    {
                        "from": "gpt",
                        "value": t,
                    },
                ],
            }
        )

        cnt += 1

    json.dump(new_data, open(args_param.output_path, "w",encoding="utf-8"), indent=2,ensure_ascii=False)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, default="alpaca-data.json")
    parser.add_argument(
        "--output_path", type=str, default="tcm-data-13-conversation.json"
    )
    args = parser.parse_args()
    main(args)

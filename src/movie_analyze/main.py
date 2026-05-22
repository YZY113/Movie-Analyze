#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
import json
from decision_tree import analyze_story_success
import os
import re

def import_from_path(module_name, file_path):
    spec = spec_from_file_location(module_name, file_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

CWD_PATH = os.path.dirname(os.path.abspath(__file__))
MODULE_DICT = {
    "Account": import_from_path("movie_analyze_lib_Account", os.path.join(CWD_PATH, "lib/Account.py")),
    "LLM": import_from_path("movie_analyze_lib_LLM", os.path.join(CWD_PATH, "lib/LLM.py")),
    "Project": import_from_path("movie_analyze_lib_Project", os.path.join(CWD_PATH, "lib/Project.py")),
}
"""
Account 變數清單
[變數] BASE_PATH         => 根目錄位置
[變數] LIB_PATH          => lib 目錄位置
[變數] INTENT_PATH       => intent 目錄位置
[變數] REPLY_PATH        => reply 目錄位置
[變數] ACCOUNT_DICT      => account.info 內容
[變數] ARTICUT           => ArticutAPI (用法：ARTICUT.parse()。 #需安裝 ArticutAPI.)
[變數] USER_DEFINED_FILE => 使用者自定詞典的檔案路徑
[變數] USER_DEFINED_DICT => 使用者自定詞典內容
"""
ACCOUNT_DICT = MODULE_DICT["Account"].ACCOUNT_DICT
ARTICUT = MODULE_DICT["Account"].ARTICUT
USER_DEFINED_FILE = MODULE_DICT["Account"].USER_DEFINED_FILE
getCosineSimilarity = MODULE_DICT["LLM"].getCosineSimilarity
getLLM = MODULE_DICT["LLM"].getLLM
COMM_TEST = MODULE_DICT["Project"].COMM_TEST
cosSimilarLoki = MODULE_DICT["Project"].cosSimilarLoki
execLoki = MODULE_DICT["Project"].execLoki


#============== Function ==============
def getSimilarity(input1STR, input2STR, featureLIST=ACCOUNT_DICT["utterance_feature"], userDefinedDictFILE=USER_DEFINED_FILE):
    """
    input
        input1STR              STR      文本1
        input2STR              STR      文本2
        featureLIST            STR[]    比對的 feature (noun, verb, contentword)
        userDefinedDictFILE    STR      使用者自定詞典的檔案路徑

    output
        score                  FLOAT    本文 1 和 2 兩者的餘弦相似度
    """
    score = getCosineSimilarity(input1STR, input2STR, featureLIST, userDefinedDictFILE)
    return score

def askLoki(content, **kwargs):
    """
    input
        content       STR / STR[]    要執行 Loki 分析的內容 (可以是字串或字串列表)
        filterLIST    STR[]          指定要比對的意圖 (空列表代表不指定)
        splitLIST     STR[]          指定要斷句的符號 (空列表代表不指定)
                                     * 如果一句 content 內包含同一意圖的多個 utterance，請使用 splitLIST 切割 content
        refDICT       DICT           參考內容
        toolkitDICT   DICT           工具箱

    output
        resultDICT    DICT           合併 runLoki() 的結果

    e.g.
        splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";"]
        resultDICT = execLoki("今天天氣如何？後天氣象如何？")                      # output => ["今天天氣"]
        resultDICT = execLoki("今天天氣如何？後天氣象如何？", splitLIST=splitLIST) # output => ["今天天氣", "後天氣象"]
        resultDICT = execLoki(["今天天氣如何？", "後天氣象如何？"])                # output => ["今天天氣", "後天氣象"]
    """
    filterLIST = kwargs["filterLIST"] if "filterLIST" in kwargs else []
    splitLIST = kwargs["splitLIST"] if "splitLIST" in kwargs else []
    refDICT = kwargs["refDICT"] if "refDICT" in kwargs else {}
    toolkitDICT = kwargs["toolkitDICT"] if "toolkitDICT" in kwargs else {}

    resultDICT = execLoki(content, filterLIST=filterLIST, splitLIST=splitLIST, refDICT=refDICT, toolkitDICT=toolkitDICT)
    return resultDICT

def askLLM(system="", assistant="", user=""):
    """
    input
        system       STR    設定 system role 的 content
        assistant    STR    設定 assistant role 的 content
        user         STR    設定 user role 的 content

    output
        response     STR    LLM 返回結果
    """
    return getLLM(system, assistant, user)

def simLoki(content, **kwargs):
    """
    input
        content       STR / STR[]    要執行 Loki Similarity 的內容 (可以是字串或字串列表)
        splitLIST     STR[]          指定要斷句的符號 (空列表代表不指定)
                                           * 如果一句 content 內包含同一意圖的多個 utterance，請使用 splitLIST 切割 content
        featureLIST   STR[]          CosineSimilarity 計算時使用的參數

    output
        resultDICT    DICT           相似度結果 {intent: input }
    """
    splitLIST = kwargs["splitLIST"] if "splitLIST" in kwargs else ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";"]
    featureLIST = kwargs["featureLIST"] if "featureLIST" in kwargs else []

    resultDICT = cosSimilarLoki(content, splitLIST=splitLIST, featureLIST=featureLIST)
    return resultDICT

def getPersonList(inputSTR, includePronounBOOL=False):
    if ARTICUT is None:
        print("ARTICUT 尚未初始化，請確認 account.info 裡有 username 和 api_key。")
        return []

    parseResultDICT = ARTICUT.parse(inputSTR, userDefinedDictFILE=USER_DEFINED_FILE)

    if not parseResultDICT.get("status"):
        print(parseResultDICT.get("msg"))
        return []

    personLIST = ARTICUT.getPersonLIST(
        parseResultDICT,
        includePronounBOOL=includePronounBOOL
    )

    return personLIST



# def detect_event_with_llm(text: str) -> dict:
#     prompt = f"""
# 你是電影文案分析師。請判斷以下文案是否包含「觸發事件（Event）」。

# 觸發事件的定義：
# - 主角原本的生活狀態被某件事打破
# - 這件事把主角捲入衝突或冒險
# - 不限句型，只看語意

# 請回答：
# 1. 有無觸發事件（是/否）
# 2. 如果有，摘錄出原句

# 只用 JSON 回答，格式：
# {{"has_event": true/false, "sentences": ["原句1", "原句2"]}}

# 文案：
# {text}
# """
#     response = getLLM(user=prompt)
#     return json.loads(response)

def detect_event_with_llm(text: str) -> dict:
    prompt = f"""
你是電影文案分析師。請判斷以下文案是否包含「觸發事件（Event）」。

觸發事件的定義：
- 主角原本的生活狀態被某件事打破
- 這件事把主角捲入衝突或冒險
- 不限句型，只看語意

只用 JSON 回答，格式：
{{"has_event": true, "sentences": ["原句1", "原句2"]}}

文案：
{text}
"""
    response = getLLM(user=prompt)

    print("LLM 原始回覆：")
    print(response)

    if not response:
        return {"has_event": False, "sentences": [], "error": "LLM 回傳空字串"}

    response = response.strip()
    response = response.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {
            "has_event": False,
            "sentences": [],
            "error": "LLM 回傳不是合法 JSON",
            "raw_response": response
        }


if __name__ == "__main__":
    from pprint import pprint

    contentSTR = input("請輸入要分析的內容：")
    contentSTR = re.sub(r"（\w+）", "", contentSTR)
    eventResultDICT = detect_event_with_llm(contentSTR)

    print("Event 判斷：")
    pprint(eventResultDICT)
    

    if not contentSTR and "utterance_count" in ACCOUNT_DICT and ACCOUNT_DICT["utterance_count"]:
        intentSTR = list(ACCOUNT_DICT["utterance_count"])[0]
        contentSTR = list(ACCOUNT_DICT["utterance_count"][intentSTR])[0]
        contentSTR = re.sub("[\[\]]", "", contentSTR)
        

        # # Articut parse
        # if ARTICUT is None:
        #     print("ARTICUT 尚未初始化，請確認 account.info 裡 username 和 api_key。")
        # else:
        #     articutResultDICT = ARTICUT.parse(contentSTR, userDefinedDictFILE=USER_DEFINED_FILE)
        #     pprint(articutResultDICT)
        

    filterLIST =  ["character"]
    splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";"]
    # 設定參考資料
    refDICT = { "character": [] }
    personLIST = getPersonList(contentSTR, includePronounBOOL=False)
    
    personNameLIST = []
    for sentencePersonLIST in personLIST:
        for _, _, personName in sentencePersonLIST:
            if personName not in personNameLIST:
                personNameLIST.append(personName)


    # 檢測功能是否正常
    #COMM_TEST(contentSTR)

    # 執行 Loki
    resultDICT = askLoki(contentSTR, filterLIST=filterLIST, splitLIST=splitLIST, refDICT=refDICT)
    for personName in personNameLIST:
        if personName not in resultDICT["character"]:
            resultDICT["character"].append(personName)
    pprint(resultDICT)

    # 執行 Decision Tree 分析故事成功率
    # treeResultDICT = analyze_story_success(resultDICT)
    # pprint(treeResultDICT)


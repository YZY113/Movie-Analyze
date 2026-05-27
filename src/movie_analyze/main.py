#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from decision_tree import analyze_story_success
import os
import re
from pathlib import Path
from pprint import pprint



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
    splitLIST = kwargs["splitLIST"] if "splitLIST" in kwargs else ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";", "、"]
    featureLIST = kwargs["featureLIST"] if "featureLIST" in kwargs else []

    resultDICT = cosSimilarLoki(content, splitLIST=splitLIST, featureLIST=featureLIST)
    return resultDICT

def remove_duplicate(inputLIST):
    resultLIST = []

    for item in inputLIST:
        if item not in resultLIST:
            resultLIST.append(item)

    return resultLIST


# def test_all_raw_character():

#     projectRootPATH = Path(__file__).resolve().parents[2]
#     rawDataPATH = projectRootPATH / "data" / "raw_data"

#     splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";", "、"]
#     filterLIST = ["character"]

#     for filePATH in sorted(rawDataPATH.glob("*.txt")):
#         contentSTR = filePATH.read_text(encoding="utf-8").strip()
#         contentSTR = re.sub(r"《[^》]*》|【[^】]*】|\([^)]*\)|（[^）]*）", "", contentSTR)

#         print(f"\n===== {filePATH.name} =====", flush=True)

#         resultDICT = askLoki(
#             contentSTR,
#             filterLIST=filterLIST,
#             splitLIST=splitLIST,
#             refDICT={"character": []}
#         )

#         print()
#         pprint({"character": resultDICT.get("character", [])})

# def test_all_raw_hero_must_do():

#     projectRootPATH = Path(__file__).resolve().parents[2]
#     rawDataPATH = projectRootPATH / "data" / "raw_data"

#     splitLIST = ["，", "。", "？", "！", "!", ",", "\n", "；", ";"]
#     filterLIST = ["Hero_must_do"]

#     for filePATH in sorted(rawDataPATH.glob("*.txt")):
#         contentSTR = filePATH.read_text(encoding="utf-8").strip()
#         contentSTR = re.sub(r"《[^》]*》|【[^】]*】|\([^)]*\)|（[^）]*）", "", contentSTR)

#         print(f"\n===== {filePATH.name} =====", flush=True)

#         resultDICT = askLoki(
#                 contentSTR,
#                 filterLIST=filterLIST,
#                 splitLIST=splitLIST,
#                 refDICT={"Hero_must_do": []}
#             )

#         print()
#         pprint({"Hero_must_do": resultDICT.get("Hero_must_do", [])})

# def test_all_raw_motivation():

#     projectRootPATH = Path(__file__).resolve().parents[2]
#     rawDataPATH = projectRootPATH / "data" / "raw_data"

#     splitLIST = ["，", "。", "？", "！", "!", ",", "\n", "；", ";"]
#     filterLIST = ["Motivation"]

#     for filePATH in sorted(rawDataPATH.glob("*.txt")):
#         contentSTR = filePATH.read_text(encoding="utf-8").strip()
#         contentSTR = re.sub(r"《[^》]*》|【[^】]*】|\([^)]*\)|（[^）]*）", "", contentSTR)

#         print(f"\n===== {filePATH.name} =====", flush=True)

#         resultDICT = askLoki(
#             contentSTR,
#             filterLIST=filterLIST,
#             splitLIST=splitLIST,
#             refDICT={"Motivation": []}
#         )

#         print()
#         pprint({"Motivation": resultDICT.get("Motivation", [])})

# def test_all_raw_threat():

#     projectRootPATH = Path(__file__).resolve().parents[2]
#     rawDataPATH = projectRootPATH / "data" / "raw_data"

#     splitLIST = ["，", "。", "？", "！", "!", ",", "\n", "；", ";"]
#     filterLIST = ["Threat"]

#     for filePATH in sorted(rawDataPATH.glob("*.txt")):
#         contentSTR = filePATH.read_text(encoding="utf-8").strip()
#         contentSTR = re.sub(r"《[^》]*》|【[^】]*】|\([^)]*\)|（[^）]*）", "", contentSTR)

#         print(f"\n===== {filePATH.name} =====", flush=True)

#         resultDICT = askLoki(
#             contentSTR,
#             filterLIST=filterLIST,
#             splitLIST=splitLIST,
#             refDICT={"Threat": []}
#         )

#         print()
#         pprint({"Threat": resultDICT.get("Threat", [])})

# def test_all_raw_event():

#     projectRootPATH = Path(__file__).resolve().parents[2]
#     rawDataPATH = projectRootPATH / "data" / "raw_data"

#     splitLIST = ["，", "。", "？", "！", "!", ",", "\n", "；", ";"]
#     filterLIST = ["Event"]

#     for filePATH in sorted(rawDataPATH.glob("*.txt")):
#         contentSTR = filePATH.read_text(encoding="utf-8").strip()
#         contentSTR = re.sub(r"《[^》]*》|【[^】]*】|\([^)]*\)|（[^）]*）", "", contentSTR)

#         print(f"\n===== {filePATH.name} =====", flush=True)

#         resultDICT = askLoki(
#             contentSTR,
#             filterLIST=filterLIST,
#             splitLIST=splitLIST,
#             refDICT={"Event": []}
#         )

#         print()
#         pprint({"Event": resultDICT.get("Event", [])})


def test_all_raw_intent():
    from pathlib import Path
    from pprint import pprint

    projectRootPATH = Path(__file__).resolve().parents[2]
    rawDataPATH = projectRootPATH / "data" / "raw_data"

    splitLIST = ["，", "。", "？", "！", "!", ",", "\n", "；", ";"]
    filterLIST = ["character", "Hero_must_do", "Motivation", "Threat", "Event"]

    for filePATH in sorted(rawDataPATH.glob("*.txt")):
        contentSTR = filePATH.read_text(encoding="utf-8").strip()
        contentSTR = re.sub(r"《[^》]*》|【[^】]*】|\([^)]*\)|（[^）]*）", "", contentSTR)

        print(f"\n===== {filePATH.name} =====", flush=True)

        resultDICT = askLoki(
            contentSTR,
            filterLIST=filterLIST,
            splitLIST=splitLIST,
            refDICT={
                "character": [],
                "Hero_must_do": [],
                "Motivation": [],
                "Threat": [],
                "Event": []
            }
        )

        for intent in filterLIST:
            resultDICT[intent] = remove_duplicate(resultDICT.get(intent, []))

        pprint({
            "character": resultDICT.get("character", []),
            "Hero_must_do": resultDICT.get("Hero_must_do", []),
            "Motivation": resultDICT.get("Motivation", []),
            "Threat": resultDICT.get("Threat", []),
            "Event": resultDICT.get("Event", [])
        })

if __name__ == "__main__":
    from pprint import pprint
    #test_all_raw_character()
    #test_all_raw_hero_must_do()
    #test_all_raw_motivation()
    #test_all_raw_threat()
    #test_all_raw_event()
    test_all_raw_intent()
    # contentSTR = input("請輸入要分析的內容：")

    # if not contentSTR and "utterance_count" in ACCOUNT_DICT and ACCOUNT_DICT["utterance_count"]:
    #     intentSTR = list(ACCOUNT_DICT["utterance_count"])[0]
    #     contentSTR = list(ACCOUNT_DICT["utterance_count"][intentSTR])[0]
    #     contentSTR = re.sub("[\[\]]", "", contentSTR)
        

    # filterLIST =  ["character"]
    # splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";", "、"]
    # # 設定參考資料
    # refDICT = { "character": [] }
    

    # 檢測功能是否正常
    #COMM_TEST(contentSTR)

    # 執行 Loki
    # resultDICT = askLoki(contentSTR, filterLIST=filterLIST, splitLIST=splitLIST, refDICT=refDICT)
    # pprint(resultDICT)

    # 執行 Decision Tree 分析故事成功率
    # treeResultDICT = analyze_story_success(resultDICT)
    # pprint(treeResultDICT)


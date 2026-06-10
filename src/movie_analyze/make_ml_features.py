import csv
import re
from pathlib import Path

from main import askLoki, flatten_unique


def clean_text(contentSTR):
    contentSTR = re.sub(r"《[^》]*》|【[^】]*】|\([^)]*\)|（[^）]*）", "", contentSTR)
    contentSTR = re.sub(r"[「」]", "", contentSTR)
    return contentSTR


def extract_features(filePATH):
    intentLIST = ["character", "Hero_must_do", "Motivation", "Threat", "Event"]
    splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";"]

    contentSTR = filePATH.read_text(encoding="utf-8").strip()
    contentSTR = clean_text(contentSTR)

    # splitPAT = re.compile("|".join(re.escape(mark) for mark in splitLIST))

    # sentenceLIST = [
    #     sentence.strip()
    #     for sentence in splitPAT.split(contentSTR)
    #     if sentence.strip()
    # ]

    # resultDICT = {intent: [] for intent in intentLIST}

    # for sentenceSTR in sentenceLIST:
    #     sentenceResultDICT = askLoki(
    #         sentenceSTR,
    #         filterLIST=intentLIST,
    #         splitLIST=[],
    #         refDICT={intent: [] for intent in intentLIST}
    #     )

    # for intent in intentLIST:
    #     resultDICT[intent].extend(sentenceResultDICT.get(intent, []))

    resultDICT = askLoki(
        contentSTR,
        filterLIST=intentLIST,
        splitLIST=splitLIST,
        refDICT={intent: [] for intent in intentLIST}
        )

    featureDICT = {
        "file": filePATH.name
    }

    for intent in intentLIST:
        itemLIST = flatten_unique(resultDICT.get(intent, []))

        featureDICT[f"has_{intent}"] = 1 if itemLIST else 0
        featureDICT[f"count_{intent}"] = len(itemLIST)

    return featureDICT


def build_feature_csv():
    projectRootPATH = Path(__file__).resolve().parents[2]
    rawDataPATH = projectRootPATH / "data" / "raw_data"
    badDataPATH = projectRootPATH / "data" / "bad_data"
    outputPATH = projectRootPATH / "data" / "ml_features.csv"

    rowLIST = []

    for filePATH in sorted(rawDataPATH.glob("*.txt")):
        featureDICT = extract_features(filePATH)
        featureDICT["label"] = "high"
        rowLIST.append(featureDICT)

    for filePATH in sorted(badDataPATH.glob("*.txt")):
        featureDICT = extract_features(filePATH)
        featureDICT["label"] = "low"
        rowLIST.append(featureDICT)

    fieldLIST = list(rowLIST[0].keys())

    with open(outputPATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldLIST)
        writer.writeheader()
        writer.writerows(rowLIST)

    print(f"saved: {outputPATH}")


if __name__ == "__main__":
    build_feature_csv()
# Movie-Analyze

Movie-Analyze 是一個用來分析電影劇情簡介的專案。專案會從電影文案中抽取角色、主角必須採取的行動、動機、威脅與事件，並整理成 JSON 格式，方便後續做規則測試、資料標註或模型分析。

## 分析目標

目前主要分析以下 intents：

- `character`：角色或人物
- `Hero_must_do`：主角必須做的事
- `Motivation`：角色行動的動機
- `Threat`：威脅或危機
- `Event`：觸發事件

## 專案結構

```text
Movie-Analyze/
├── README.md
├── data_wash.py
├── data/
│   ├── raw_data/          # 原始電影文案
│   ├── processed_data/    # 已整理或標註過的 JSON 資料
│   └── test_data/         # 測試用 JSON 資料
├── src/
│   └── movie_analyze/
│       ├── main.py        # 主要測試與執行程式
│       ├── decision_tree.py
│       ├── requirements.txt
│       └── intent/
│           ├── Loki_character.py
│           ├── Loki_Hero_must_do.py
│           ├── Loki_Motivation.py
│           ├── Loki_Threat.py
│           ├── Loki_Event.py
│           └── USER_DEFINED.json
└── ref/                   # 參考資料
```

## Data Wash

`data_wash.py` 會從 `data/raw_data` 裡的電影文案抽取專有名詞，例如：

- 電影名稱，例如：`《雷神索爾：愛與雷霆》`
- 演員名稱，例如：`（克里斯漢斯沃飾）`

抽出的詞會寫入：

```text
src/movie_analyze/intent/USER_DEFINED.json
```

讓 Articut / Loki 在分析時可以更正確辨識電影名稱、演員名稱等專有名詞，降低斷詞錯誤。

## 執行方式

安裝套件：

```bash
pip install -r src/movie_analyze/requirements.txt
```

執行 data wash：

```bash
python data_wash.py
```

執行主要程式：

```bash
python src/movie_analyze/main.py
```

## 測試 Intent

可以在 `main.py` 裡設定 `filterLIST` 來測試指定 intent。

只測試 `character`：

```python
filterLIST = ["character"]
```

測試除了 `Event` 之外的所有 intent：

```python
filterLIST = ["character", "Hero_must_do", "Motivation", "Threat"]
```

測試所有 intent：

```python
filterLIST = ["character", "Hero_must_do", "Motivation", "Threat", "Event"]
```

如果分析結果有重複項目，可以使用：

```python
def remove_duplicate(inputLIST):
    resultLIST = []

    for item in inputLIST:
        if item not in resultLIST:
            resultLIST.append(item)

    return resultLIST
```

再對指定 intent 去重：

```python
resultDICT["Threat"] = remove_duplicate(resultDICT.get("Threat", []))
```

若要對所有 intent 去重：

```python
intentLIST = ["character", "Hero_must_do", "Motivation", "Threat", "Event"]

for intent in intentLIST:
    resultDICT[intent] = remove_duplicate(resultDICT.get(intent, []))
```

## 輸出格式

每部電影的分析結果會整理成 JSON，例如：

```json
{
  "蜘蛛人：新宇宙": {
    "character": {
      "utterance": ["布魯克林的青少年邁爾斯摩拉斯"]
    },
    "Hero_must_do": {
      "utterance": ["必須運用他新獲得的能力"]
    },
    "Motivation": {
      "utterance": [""]
    },
    "Threat": {
      "utterance": ["對抗邪惡的「金霸王」"]
    },
    "Event": {
      "utterance": ["在地鐵裡被一隻放射性蜘蛛咬傷後"]
    }
  }
}
```

## 測試資料

`data/test_data` 目前放測試用 JSON，例如：

- `test_data_Movie14.json`
- `test_data_Movie22.json`
- `test_data_Movie26.json`

這些檔案可以用來檢查 intent 輸出是否符合預期標註。

## 注意事項

- `USER_DEFINED.json` 會影響 Articut / Loki 的斷詞與 intent 分析結果。
- 更新 `USER_DEFINED.json` 後，如果 `processed_data` 是由舊字典產生的分析結果，建議重新檢查。
- `__pycache__` 是 Python 自動產生的快取資料夾，不需要提交。
- `account.info` 可能包含 API key，不應該上傳到 GitHub。
- intent key 建議統一使用 `Hero_must_do` 和 `Motivation`，避免使用 `hero_must_do` 或 `movtivation`。

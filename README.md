# Movie-Analyze

Movie-Analyze 是一個以超級英雄電影文案為語料的敘事特徵分析專案。專案使用 Articut / Loki 規則系統抽取五個語言學敘事特徵，並進一步將抽取結果轉成機器學習特徵，用 Decision Tree、Logistic Regression、SVM、KNN 分類電影文案的 `high / low` 類別。

本專案的核心不是單純追求分類準確率，而是建立一套可解釋的語言學分析流程：先用 Loki 把電影文案轉成敘事特徵，再用機器學習模型檢驗這些特徵是否具有分類能力。

## Research Flow

```text
電影文案
↓
Data Wash 更新自訂詞
↓
Loki / Articut 規則分析
↓
五大敘事特徵
↓
Precision / Recall / F1 評估
↓
Feature Vector
↓
Decision Tree / Logistic Regression / SVM / KNN
↓
high / low 分類結果
```

本專案也建立 raw text baseline：

```text
原始電影文案
↓
TF-IDF 向量化
↓
Decision Tree / Logistic Regression / SVM / KNN
↓
high / low 分類結果
```

## Five Narrative Features

| Intent | 說明 |
|---|---|
| `character` | 文案中的角色、英雄、反派或重要人物 |
| `Hero_must_do` | 英雄或主角必須完成的任務、行動或責任 |
| `Motivation` | 角色行動背後的原因、目的或動機 |
| `Threat` | 威脅、敵人、危機或破壞力量 |
| `Event` | 故事事件、背景變化或情節推進 |

## Project Structure

```text
Movie-Analyze/
├── README.md
├── data_wash.py
├── data/
│   ├── raw_data/          # 原始電影文案，作為 high 類別
│   ├── bad_data/          # 對照文案，作為 low 類別
│   ├── test_data/         # Loki 評估用 gold standard
│   ├── processed_data/    # 整理後的 JSON 資料
│   └── ml_features.csv    # Loki feature vector
└── src/
    └── movie_analyze/
        ├── main.py
        ├── make_ml_features.py
        ├── train_decision_tree.py
        ├── train_logistic_regression.py
        ├── train_svm.py
        ├── train_knn.py
        ├── train_raw_text_baseline.py
        ├── requirements.txt
        └── intent/
            ├── Loki_character.py
            ├── Loki_Hero_must_do.py
            ├── Loki_Motivation.py
            ├── Loki_Threat.py
            ├── Loki_Event.py
            └── USER_DEFINED.json
```

## Setup

Install Articut / Loki dependencies:

```bash
pip install -r src/movie_analyze/requirements.txt
```

Install machine learning dependencies:

```bash
pip install pandas scikit-learn
```

The Loki API setting is stored in:

```text
src/movie_analyze/account.info
```

If debug output such as `[character] ... ===>` is not needed, set:

```json
"debug": false
```

Use valid JSON booleans: `true` / `false`, not Python `True` / `False`.

## Data Wash

`data_wash.py` extracts movie names and actor names from `data/raw_data` and merges them into:

```text
src/movie_analyze/intent/USER_DEFINED.json
```

This helps Articut / Loki recognize movie titles, actor names, and proper nouns more accurately.

Preview without changing `USER_DEFINED.json`:

```bash
python data_wash.py --dry-run
```

Update `USER_DEFINED.json`:

```bash
python data_wash.py
```

Example output:

```text
extract _movieName: 14
extract _actorName: 29
merged _movieName: 60
merged _actorName: 66
updated: src/movie_analyze/intent/USER_DEFINED.json
```

## Loki Evaluation

`data/test_data` is used as the gold standard. Each JSON file contains the correct utterances for the five intents.

Run evaluation:

```bash
python src/movie_analyze/main.py
```

The evaluation reports per-intent:

| Metric | 說明 |
|---|---|
| `TP` | Loki 抓到，且 gold standard 也有 |
| `FP` | Loki 多抓，但 gold standard 沒有 |
| `FN` | gold standard 有，但 Loki 沒抓到 |
| `precision` | 抓到的結果中，有多少是正確的 |
| `recall` | gold standard 中，有多少被抓到 |
| `f1` | precision 與 recall 的綜合指標 |

Current matching rule:

```python
predSTR == goldSTR
```

This means the prediction and gold standard must be exactly the same to count as a match.

## Loki Feature Vector

Generate machine learning features from Loki outputs:

```bash
python src/movie_analyze/make_ml_features.py
```

This creates:

```text
data/ml_features.csv
```

Each movie is converted into features such as:

```text
has_character
count_character
has_Hero_must_do
count_Hero_must_do
has_Motivation
count_Motivation
has_Threat
count_Threat
has_Event
count_Event
label
```

Labels are assigned as:

```text
data/raw_data  -> high
data/bad_data  -> low
```

## Machine Learning Models

All four models use the same Loki feature vector: `data/ml_features.csv`.

Run Decision Tree:

```bash
python src/movie_analyze/train_decision_tree.py
```

Run Logistic Regression:

```bash
python src/movie_analyze/train_logistic_regression.py
```

Run SVM:

```bash
python src/movie_analyze/train_svm.py
```

Run KNN:

```bash
python src/movie_analyze/train_knn.py
```

The data is split with:

```python
test_size=0.25
random_state=42
stratify=y
```

This means 75% of the data is used for training and 25% is used for testing.

## Raw Text Baseline

The baseline uses raw movie text instead of Loki features. Text is converted into TF-IDF character n-gram features and then classified with the same four models.

Run baseline:

```bash
python src/movie_analyze/train_raw_text_baseline.py
```

The baseline is useful for comparison:

```text
Loki features     -> interpretable narrative features
Raw text TF-IDF   -> surface-level text features
```

## Current Experiment Summary

One experiment result using Loki features:

| Model | Accuracy | Macro F1 |
|---|---:|---:|
| Decision Tree | 0.818 | 0.812 |
| Logistic Regression | 0.727 | 0.705 |
| SVM | 0.682 | 0.646 |
| KNN | 0.818 | 0.741 |

One experiment result using raw TF-IDF baseline:

| Model | Accuracy | Macro F1 |
|---|---:|---:|
| Decision Tree | 0.727 | 0.686 |
| Logistic Regression | 0.818 | 0.741 |
| SVM | 0.818 | 0.741 |
| KNN | 0.818 | 0.771 |

Decision Tree with Loki features is especially useful because it provides interpretable rules. For example, the model can show whether `count_character` or `has_Event` helps distinguish `high` and `low` movie descriptions.

## Research Interpretation

In this project, Loki and machine learning are connected as follows:

```text
Loki = linguistic feature extractor
Machine learning models = classifier / predictor
```

Loki extracts the five narrative features from movie descriptions. The extracted features are then transformed into a feature vector and passed into machine learning models.

This preserves the linguistic focus of the project. Instead of directly feeding raw text into a black-box model, the system first converts text into interpretable narrative features.

## Notes

- `USER_DEFINED.json` improves proper noun recognition.
- If Loki rules are updated, run `make_ml_features.py` again before retraining ML models.
- Improving Loki recall may change the ML model results, but the two recall values are not the same metric.
- `__pycache__` is Python's cache folder and can be ignored.
- API keys in `account.info` should not be shared publicly.

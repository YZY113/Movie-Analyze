from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier


def print_cv_result(modelName, scoreDICT):
    print(f"\n===== {modelName} =====")

    for metric in ["accuracy", "precision_macro", "recall_macro", "f1_macro"]:
        scoreLIST = scoreDICT[f"test_{metric}"]
        print(f"{metric}: {scoreLIST.mean():.4f} (+/- {scoreLIST.std():.4f})")


def load_text_data():
    projectRootPATH = Path(__file__).resolve().parents[2]
    rawDataPATH = projectRootPATH / "data" / "raw_data"
    badDataPATH = projectRootPATH / "data" / "bad_data"

    textLIST = []
    labelLIST = []

    for filePATH in sorted(rawDataPATH.glob("*.txt")):
        textLIST.append(filePATH.read_text(encoding="utf-8"))
        labelLIST.append("high")

    for filePATH in sorted(badDataPATH.glob("*.txt")):
        textLIST.append(filePATH.read_text(encoding="utf-8"))
        labelLIST.append("low")

    return textLIST, labelLIST


def train_raw_text_cv():
    X, y = load_text_data()

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    scoring = [
        "accuracy",
        "precision_macro",
        "recall_macro",
        "f1_macro"
    ]

    modelDICT = {
        "Raw TF-IDF + Decision Tree": DecisionTreeClassifier(
            max_depth=3,
            random_state=42,
            class_weight="balanced"
        ),

        "Raw TF-IDF + Logistic Regression": LogisticRegression(
            class_weight="balanced",
            random_state=42,
            max_iter=1000
        ),

        "Raw TF-IDF + SVM": SVC(
            kernel="linear",
            class_weight="balanced",
            random_state=42
        ),

        "Raw TF-IDF + KNN": KNeighborsClassifier(
            n_neighbors=3
        )
    }

    for modelName, model in modelDICT.items():
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                analyzer="char",
                ngram_range=(2, 4),
                max_features=1000
            )),
            ("classifier", model)
        ])

        scoreDICT = cross_validate(
            pipeline,
            X,
            y,
            cv=cv,
            scoring=scoring
        )

        print_cv_result(modelName, scoreDICT)


if __name__ == "__main__":
    train_raw_text_cv()
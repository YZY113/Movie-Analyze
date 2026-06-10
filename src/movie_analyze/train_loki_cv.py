import pandas as pd

from pathlib import Path
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier


def print_cv_result(modelName, scoreDICT):
    print(f"\n===== {modelName} =====")

    for metric in ["accuracy", "precision_macro", "recall_macro", "f1_macro"]:
        scoreLIST = scoreDICT[f"test_{metric}"]
        print(f"{metric}: {scoreLIST.mean():.4f} (+/- {scoreLIST.std():.4f})")


def train_loki_cv():
    projectRootPATH = Path(r"C:\Users\user\Desktop\Movie-Analyze")
    featurePATH = projectRootPATH / "data" / "ml_features.csv"

    df = pd.read_csv(featurePATH)

    X = df.drop(columns=["file", "label"])
    y = df["label"]

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
        "Loki Features + Decision Tree": DecisionTreeClassifier(
            max_depth=3,
            random_state=42,
            class_weight="balanced"
        ),

        "Loki Features + Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(
                class_weight="balanced",
                random_state=42,
                max_iter=1000
            ))
        ]),

        "Loki Features + SVM": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", SVC(
                kernel="linear",
                class_weight="balanced",
                random_state=42
            ))
        ]),

        "Loki Features + KNN": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", KNeighborsClassifier(
                n_neighbors=3
            ))
        ])
    }

    for modelName, model in modelDICT.items():
        scoreDICT = cross_validate(
            model,
            X,
            y,
            cv=cv,
            scoring=scoring
        )

        print_cv_result(modelName, scoreDICT)


if __name__ == "__main__":
    train_loki_cv()
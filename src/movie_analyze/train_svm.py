import pandas as pd

from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def train_svm():
    projectRootPATH = Path(__file__).resolve().parents[2]
    featurePATH = projectRootPATH / "data" / "ml_features.csv"

    df = pd.read_csv(featurePATH)

    X = df.drop(columns=["file", "label"])
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", SVC(
            kernel="linear",
            class_weight="balanced",
            random_state=42
        ))
    ])

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("===== SVM =====")
    print("accuracy:", accuracy_score(y_test, y_pred))
    print("precision:", precision_score(y_test, y_pred, average="macro"))
    print("recall:", recall_score(y_test, y_pred, average="macro"))
    print("f1:", f1_score(y_test, y_pred, average="macro"))

    print("\n===== Classification Report =====")
    print(classification_report(y_test, y_pred))

    print("\n===== Confusion Matrix =====")
    print(confusion_matrix(y_test, y_pred))

    print("\n===== Feature Weights =====")
    classifier = model.named_steps["classifier"]
    print("classes:", classifier.classes_)

    weightLIST = list(zip(X.columns, classifier.coef_[0]))
    weightLIST = sorted(weightLIST, key=lambda x: abs(x[1]), reverse=True)

    for feature, weight in weightLIST:
        print(f"{feature}: {weight:.4f}")


if __name__ == "__main__":
    train_svm()
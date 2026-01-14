# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.model_selection import train_test_split

DATA_PATH = Path("data/raw/sensor_data.csv")
MODEL_PATH = Path("models/modelo_preditivo.pkl")


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {path}")
    return pd.read_csv(path)


def train_model(df: pd.DataFrame) -> RandomForestClassifier:
    features = [
        "temperatura",
        "rotacao_rpm",
        "vibracao_mm_s",
        "pressao_bar",
    ]
    X = df[features]
    y = df["falha"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        n_jobs=-1,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print("Matriz de confusão:\n", cm)
    print(f"F1-Score: {f1:.3f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Modelo salvo em {MODEL_PATH.resolve()}")

    return model


def main():
    df = load_data()
    train_model(df)


if __name__ == "__main__":
    main()

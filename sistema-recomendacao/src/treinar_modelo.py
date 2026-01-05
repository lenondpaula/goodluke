from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
from surprise import Dataset, Reader, SVD, dump

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "avaliacoes.csv"
PRODUTOS_PATH = BASE_DIR / "data" / "produtos.csv"
MODEL_PATH = BASE_DIR / "models" / "recommender.pkl"

RATING_SCALE = (1, 5)
RANDOM_STATE = 42


def carregar_dados() -> Tuple[pd.DataFrame, Dataset]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Arquivo de avaliações não encontrado: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    reader = Reader(rating_scale=RATING_SCALE)
    data = Dataset.load_from_df(df[["user_id", "product_id", "rating"]], reader)
    return df, data


def treinar_modelo() -> SVD:
    df, data = carregar_dados()
    trainset = data.build_full_trainset()

    model = SVD(random_state=RANDOM_STATE)
    model.fit(trainset)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    dump.dump(str(MODEL_PATH), algo=model)
    print(f"Modelo salvo em {MODEL_PATH}")
    return model


def carregar_modelo() -> SVD:
    if MODEL_PATH.exists():
        _, loaded_model = dump.load(str(MODEL_PATH))
        return loaded_model
    raise FileNotFoundError("Modelo não encontrado. Execute treinar_modelo() primeiro.")


def obter_recomendacoes(user_id: int, n: int = 5, model: Optional[SVD] = None) -> pd.DataFrame:
    """Retorna top-N produtos não avaliados com maior nota prevista."""
    if model is None:
        model = carregar_modelo()

    produtos_df = pd.read_csv(PRODUTOS_PATH)
    avaliacoes_df = pd.read_csv(DATA_PATH)

    avaliados = set(avaliacoes_df.loc[avaliacoes_df["user_id"] == user_id, "product_id"].tolist())
    candidatos = produtos_df[~produtos_df["product_id"].isin(avaliados)].copy()

    if candidatos.empty:
        return pd.DataFrame()

    # Previsão das notas para os produtos não avaliados
    candidatos["pred_rating"] = candidatos["product_id"].apply(
        lambda pid: model.predict(uid=user_id, iid=pid).est
    )

    recomendados = (
        candidatos.sort_values("pred_rating", ascending=False)
        .head(n)
        .copy()
    )
    recomendados["segmento"] = recomendados["is_popular"].map({True: "Best-seller", False: "Long Tail"})
    return recomendados[["product_id", "nome", "categoria", "segmento", "pred_rating"]]


if __name__ == "__main__":
    modelo = treinar_modelo()
    exemplo = obter_recomendacoes(user_id=1, n=5, model=modelo)
    print("Top-5 recomendações para usuário 1:")
    print(exemplo)

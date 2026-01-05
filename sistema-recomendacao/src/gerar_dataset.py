from pathlib import Path
import numpy as np
import pandas as pd


RNG_SEED = 42
NUM_USERS = 1000
NUM_PRODUCTS = 500
NUM_RATINGS = 10_000
POPULAR_SHARE = 0.20  # 20% dos produtos
POPULAR_RATING_SHARE = 0.60  # 60% das avaliações vão para produtos populares

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
PRODUTOS_PATH = DATA_DIR / "produtos.csv"
AVALIACOES_PATH = DATA_DIR / "avaliacoes.csv"


def _criar_produtos(rng: np.random.Generator) -> pd.DataFrame:
    num_populares = int(NUM_PRODUCTS * POPULAR_SHARE)
    produtos = []

    categorias_pop = ["Eletrônicos", "Informática", "Áudio", "Casa Inteligente"]
    categorias_nicho = ["Acessórios Vintage", "Casa & Lazer", "Escritório Criativo", "Colecionáveis"]

    for pid in range(1, NUM_PRODUCTS + 1):
        if pid <= num_populares:
            nome = f"Smartphone X {pid:03d}" if pid % 2 == 0 else f"Gadget Pro {pid:03d}"
            categoria = rng.choice(categorias_pop)
            is_popular = True
        else:
            nome = f"Cabo Vintage {pid:03d}" if pid % 2 == 0 else f"Acessório Criativo {pid:03d}"
            categoria = rng.choice(categorias_nicho)
            is_popular = False
        produtos.append({
            "product_id": pid,
            "nome": nome,
            "categoria": categoria,
            "is_popular": is_popular,
        })

    return pd.DataFrame(produtos)


def _gerar_avaliacoes(rng: np.random.Generator, produtos: pd.DataFrame) -> pd.DataFrame:
    num_populares = produtos[produtos["is_popular"]]["product_id"].tolist()
    num_nicho = produtos[~produtos["is_popular"]]["product_id"].tolist()

    n_pop = int(NUM_RATINGS * POPULAR_RATING_SHARE)
    n_nicho = NUM_RATINGS - n_pop

    # Distribuição de notas (tendência mais alta para populares)
    notas_pop = rng.choice([3, 4, 5], size=n_pop, p=[0.15, 0.35, 0.50])
    notas_nicho = rng.choice([2, 3, 4, 5], size=n_nicho, p=[0.10, 0.30, 0.40, 0.20])

    # Datas aleatórias para simular ordem temporal
    datas = pd.date_range(end=pd.Timestamp.now(), periods=NUM_RATINGS, freq="h")
    rng.shuffle(datas.values)

    avaliacoes_pop = pd.DataFrame({
        "user_id": rng.integers(1, NUM_USERS + 1, size=n_pop),
        "product_id": rng.choice(num_populares, size=n_pop, replace=True),
        "rating": notas_pop,
        "timestamp": datas[:n_pop],
    })

    avaliacoes_nicho = pd.DataFrame({
        "user_id": rng.integers(1, NUM_USERS + 1, size=n_nicho),
        "product_id": rng.choice(num_nicho, size=n_nicho, replace=True),
        "rating": notas_nicho,
        "timestamp": datas[n_pop:],
    })

    avaliacoes = pd.concat([avaliacoes_pop, avaliacoes_nicho], ignore_index=True)
    avaliacoes.sort_values("timestamp", inplace=True)
    avaliacoes.reset_index(drop=True, inplace=True)
    return avaliacoes


def gerar():
    rng = np.random.default_rng(RNG_SEED)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    produtos = _criar_produtos(rng)
    avaliacoes = _gerar_avaliacoes(rng, produtos)

    produtos.to_csv(PRODUTOS_PATH, index=False)
    avaliacoes.to_csv(AVALIACOES_PATH, index=False)
    print(f"Dados salvos em {PRODUTOS_PATH} e {AVALIACOES_PATH}")


if __name__ == "__main__":
    gerar()

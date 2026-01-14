# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
Vitrine inteligente "Que tal esse?"
Dashboard Streamlit que consome o modelo SVD treinado com Surprise
para recomendar itens de cauda longa em um e-commerce fictício.
"""

from pathlib import Path
import sys
from typing import Tuple

import numpy as np
import pandas as pd
import streamlit as st
from surprise import dump

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
MODEL_PATH = BASE_DIR / "models" / "recommender.pkl"
PRODUTOS_PATH = DATA_DIR / "produtos.csv"
AVALIACOES_PATH = DATA_DIR / "avaliacoes.csv"

# Importa componentes compartilhados
sys.path.insert(0, str(PROJECT_ROOT))
from shared.components import (  # noqa: E402
    SHARED_SIDEBAR_CSS,
    render_sidebar_navegacao,
    render_rodape,
    render_instrucoes_uso,
)


def _ensure_paths() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)


@st.cache_data(show_spinner=False)
def carregar_dados() -> Tuple[pd.DataFrame, pd.DataFrame]:
    _ensure_paths()
    produtos = pd.read_csv(PRODUTOS_PATH)
    avaliacoes = pd.read_csv(AVALIACOES_PATH)
    avaliacoes["timestamp"] = pd.to_datetime(avaliacoes["timestamp"])
    return produtos, avaliacoes


@st.cache_resource(show_spinner=False)
def carregar_modelo():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Modelo não encontrado. Treine primeiro com treinar_modelo.py.")
    _, model = dump.load(str(MODEL_PATH))
    return model


def _ultimas_avaliacoes(avaliacoes: pd.DataFrame, produtos: pd.DataFrame, user_id: int) -> pd.DataFrame:
    ult = (
        avaliacoes[avaliacoes["user_id"] == user_id]
        .sort_values("timestamp", ascending=False)
        .head(5)
        .merge(produtos, on="product_id", how="left")
    )
    return ult[["timestamp", "nome", "categoria", "rating", "is_popular"]]


def _recomendar(produtos: pd.DataFrame, avaliacoes: pd.DataFrame, user_id: int, n: int = 6) -> pd.DataFrame:
    model = carregar_modelo()
    avaliados = set(avaliacoes.loc[avaliacoes["user_id"] == user_id, "product_id"].tolist())
    candidatos = produtos[~produtos["product_id"].isin(avaliados)].copy()

    if candidatos.empty:
        return pd.DataFrame()

    candidatos["pred_rating"] = candidatos["product_id"].apply(
        lambda pid: model.predict(uid=user_id, iid=int(pid)).est
    )

    recs = candidatos.sort_values("pred_rating", ascending=False).head(n).copy()
    recs["segmento"] = recs["is_popular"].map({True: "Best-seller", False: "Long Tail"})
    return recs[["product_id", "nome", "categoria", "segmento", "pred_rating", "is_popular"]]


def _calcular_uplift(ult: pd.DataFrame, recs: pd.DataFrame) -> float:
    if recs.empty:
        return 0.0
    base = ult["rating"].mean() if not ult.empty else 3.2
    rec_mean = recs["pred_rating"].mean()
    uplift = max(rec_mean - base, 0)
    # Converte diferença de nota (1 a 5) em percentual aproximado de ticket
    return round((uplift / 5) * 100, 1)


def _render_cards(recs: pd.DataFrame) -> None:
    cols = st.columns(3)
    for idx, (_, row) in enumerate(recs.iterrows()):
        col = cols[idx % 3]
        tag_color = "#22c55e" if not row["is_popular"] else "#0ea5e9"
        tag_label = "Long Tail" if not row["is_popular"] else "Best-seller"
        col.markdown(
            f"""
            <div style="border:1px solid #e2e8f0; border-radius:12px; padding:1rem; margin-bottom:1rem; background:#fff;">
                <div style="font-weight:700; color:#0f172a; font-size:1rem;">{row['nome']}</div>
                <div style="color:#334155; font-size:0.9rem;">{row['categoria']}</div>
                <div style="margin:0.5rem 0;">
                    <span style="background:{tag_color}20; color:{tag_color}; padding:0.15rem 0.55rem; border-radius:12px; font-size:0.75rem;">{tag_label}</span>
                </div>
                <div style="font-size:0.9rem; color:#475569;">Nota prevista: <strong>{row['pred_rating']:.2f}</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_app() -> None:
    st.markdown(SHARED_SIDEBAR_CSS, unsafe_allow_html=True)
    
    produtos, avaliacoes = carregar_dados()
    user_ids = sorted(avaliacoes["user_id"].unique())

    with st.sidebar:
        st.header("👤 Selecione o usuário")
        user_id = st.sidebar.selectbox("ID de Usuário", user_ids, index=0)
        st.sidebar.info("Dica: recomendamos itens de cauda longa (Long Tail) para elevar o ticket médio.")

    st.title("🛒 Que tal esse? — Recomendador de Varejo")
    st.markdown("Filtragem colaborativa com SVD para sugerir itens de nicho que aumentam o ticket médio.")

    # Instruções de uso
    render_instrucoes_uso(
        instrucoes=[
            "Selecione um ID de usuário na sidebar",
            "Veja os produtos já avaliados por este cliente",
            "Confira as recomendações personalizadas de Long Tail",
        ],
        ferramentas_sidebar=[
            "**ID de Usuário**: Escolha o cliente para receber recomendações",
            "**Dica**: Itens Long Tail elevam o ticket médio",
        ]
    )

    ult = _ultimas_avaliacoes(avaliacoes, produtos, user_id)
    recs = _recomendar(produtos, avaliacoes, user_id, n=6)
    uplift_pct = _calcular_uplift(ult, recs)

    st.markdown("---")
    st.subheader("📌 Últimos produtos avaliados")
    if ult.empty:
        st.warning("Este usuário ainda não avaliou nada. Gerando recomendações mesmo assim.")
    else:
        ult_view = ult.copy()
        ult_view["timestamp"] = ult_view["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
        ult_view.rename(columns={"timestamp": "Quando", "nome": "Produto", "categoria": "Categoria", "rating": "Nota"}, inplace=True)
        st.dataframe(ult_view[["Quando", "Produto", "Categoria", "Nota"]], hide_index=True, use_container_width=True)

    st.markdown("---")
    st.subheader("🤖 Recomendados para você")
    if recs.empty:
        st.info("Não encontramos recomendações. Verifique se há produtos disponíveis.")
    else:
        _render_cards(recs)

    st.markdown("---")
    st.subheader("💰 Potencial de aumento de ticket médio")
    col1, col2 = st.columns(2)
    col1.metric("Uplift estimado", f"+{uplift_pct}%")
    col2.write("Os itens de cauda longa sugeridos ajudam a destravar estoque e elevar o ticket médio sem depender só dos best-sellers.")

    # Menu de navegação
    render_sidebar_navegacao(app_atual=3)

    # Rodapé
    render_rodape(
        titulo_app="🛒 Que tal esse? — Recomendador",
        subtitulo="Filtragem colaborativa para descoberta de itens de nicho",
        tecnologias="SVD (Surprise) + Pandas + Streamlit"
    )


def main():
    st.set_page_config(
        page_title="Que tal esse? | Recomendador",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    render_app()


if __name__ == "__main__":
    sys.path.append(str(BASE_DIR))
    main()

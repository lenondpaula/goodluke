from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

# Caminho para o modelo - ajustado para a raiz do projeto
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "modelo_preditivo.pkl"

# ────────────────────────────────────────────────────────────────────────────────
# CSS corporativo minimalista
# ────────────────────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
:root {
    --primary: #0f172a;
    --secondary: #334155;
    --accent: #3b82f6;
    --success: #22c55e;
    --danger: #ef4444;
    --bg: #f8fafc;
}
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
.block-container {
    padding-top: 2rem;
    max-width: 900px;
}
h1 {
    color: var(--primary);
    font-weight: 700;
    letter-spacing: -0.5px;
}
section[data-testid="stSidebar"] {
    background: var(--primary);
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] label {
    font-weight: 500;
}
.status-card {
    border-radius: 12px;
    padding: 1.5rem 2rem;
    text-align: center;
    font-size: 1.25rem;
    font-weight: 600;
    margin-top: 1rem;
}
.status-ok {
    background: linear-gradient(135deg, #d1fae5, #a7f3d0);
    color: #065f46;
    border: 1px solid #34d399;
}
.status-danger {
    background: linear-gradient(135deg, #fee2e2, #fecaca);
    color: #991b1b;
    border: 1px solid #f87171;
}
.gauge-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 1rem;
}
.gauge-value {
    font-size: 3rem;
    font-weight: 700;
}
.gauge-label {
    font-size: 0.875rem;
    color: var(--secondary);
}
</style>
"""


def load_model():
    if not MODEL_PATH.exists():
        st.error(f"Modelo não encontrado em {MODEL_PATH}")
        return None
    return joblib.load(MODEL_PATH)


def layout():
    st.set_page_config(
        page_title="Sistema de Precaução Mecânica",
        page_icon="🔧",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.title("🔧 Sistema de Precaução Mecânica")
    st.markdown(
        "Ajuste os parâmetros na barra lateral para simular o estado atual do equipamento.",
    )

    # ── Apresentação ────────────────────────────────────────────────────────────
    with st.container():
        st.markdown(
            """
            <div style="background:#f1f5f9; border-left:4px solid #3b82f6; padding:1rem 1.25rem; border-radius:6px; margin-bottom:1.5rem;">
                <strong>O que é?</strong><br>
                Este painel utiliza <em>Machine Learning</em> para prever falhas em equipamentos industriais
                com base em leituras de temperatura, rotação, vibração e pressão.<br><br>
                <strong>Aplicações</strong><br>
                • Indústrias de manufatura e processos contínuos<br>
                • Monitoramento de compressores, bombas e motores<br>
                • Redução de paradas não programadas e custos de manutenção corretiva
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.sidebar:
        st.header("Parâmetros")
        temperatura = st.slider("Temperatura (°C)", 40.0, 120.0, 70.0, 0.5)
        rotacao = st.slider("Rotação (RPM)", 1200, 2600, 1800, 50)
        vibracao = st.slider("Vibração (mm/s)", 0.0, 80.0, 30.0, 0.5)
        pressao = st.slider("Pressão (bar)", 6.0, 20.0, 12.0, 0.5)

    return {
        "temperatura": temperatura,
        "rotacao_rpm": rotacao,
        "vibracao_mm_s": vibracao,
        "pressao_bar": pressao,
    }


def render_gauge(prob: float):
    """Indicador visual de probabilidade de falha."""
    color = "#22c55e" if prob < 0.5 else "#ef4444"
    pct = int(prob * 100)
    st.markdown(
        f"""
        <div class="gauge-container">
            <div class="gauge-value" style="color:{color}">{pct}%</div>
            <div class="gauge-label">Probabilidade de Falha</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_alert(prediction: int):
    if prediction == 1:
        st.markdown(
            '<div class="status-card status-danger">🚨 RISCO DE FALHA IMINENTE</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-card status-ok">✅ OPERAÇÃO NORMAL</div>',
            unsafe_allow_html=True,
        )


def main():
    inputs = layout()
    model = load_model()
    if model is None:
        st.stop()

    features = pd.DataFrame([inputs])
    pred = int(model.predict(features)[0])
    prob = float(model.predict_proba(features)[0][1])

    col1, col2 = st.columns([1, 1])
    with col1:
        render_gauge(prob)
    with col2:
        render_alert(pred)

    with st.expander("📊 Detalhes dos parâmetros"):
        st.dataframe(
            features.T.rename(columns={0: "Valor"}),
            use_container_width=True,
        )

    # ── Rodapé ──────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align:center; color:#64748b; font-size:0.85rem;">
            Desenvolvido por <strong>Lenon de Paula</strong> · 
            <a href="mailto:lenondpaula@gmail.com" style="color:#3b82f6;">lenondpaula@gmail.com</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

from pathlib import Path
import numpy as np
import pandas as pd


def gerar_dados(num_rows: int = 2000, output_path: str = "data/raw/sensor_data.csv") -> None:
    """Simula dados de sensores industriais e salva em CSV."""

    rng = np.random.default_rng(42)
    timestamps = pd.date_range(end=pd.Timestamp.now(), periods=num_rows, freq="min")

    # ~30% de registros em condição crítica para balancear classes
    n_critico = int(num_rows * 0.30)
    n_normal = num_rows - n_critico

    temp_normal = rng.normal(loc=68, scale=8, size=n_normal).clip(min=40, max=84)
    temp_critico = rng.normal(loc=92, scale=5, size=n_critico).clip(min=86)
    temperatura = np.concatenate([temp_normal, temp_critico])

    vib_normal = rng.normal(loc=28, scale=6, size=n_normal).clip(min=5, max=44)
    vib_critico = rng.normal(loc=52, scale=5, size=n_critico).clip(min=46)
    vibracao = np.concatenate([vib_normal, vib_critico])

    rotacao_rpm = rng.normal(loc=1800, scale=200, size=num_rows).clip(min=1200)
    pressao_bar = rng.normal(loc=12, scale=2, size=num_rows).clip(min=6)

    # Embaralhar ordem
    idx = rng.permutation(num_rows)
    temperatura = temperatura[idx]
    vibracao = vibracao[idx]
    rotacao_rpm = rotacao_rpm[idx]
    pressao_bar = pressao_bar[idx]

    cond_falha = (temperatura > 85) & (vibracao > 45)
    ruido = rng.binomial(1, 0.02, size=num_rows)
    falha = np.where(cond_falha, 1, ruido)

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "id_maquina": rng.integers(1, 6, size=num_rows),
            "temperatura": temperatura.round(2),
            "rotacao_rpm": rotacao_rpm.round(0).astype(int),
            "vibracao_mm_s": vibracao.round(2),
            "pressao_bar": pressao_bar.round(2),
            "falha": falha,
        }
    )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Dados simulados salvos em {output_file.resolve()}")


def main():
    gerar_dados()


if __name__ == "__main__":
    main()

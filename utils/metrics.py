import numpy as np
import pandas as pd


def clamp(value, low=0, high=100):
    return max(low, min(high, value))


def normalize(value, low, high, inverse=False):
    """Normaliza uma variável para escala 0-100."""
    if pd.isna(value):
        return 50
    score = 100 * (value - low) / (high - low)
    score = clamp(score)
    return 100 - score if inverse else score


def readiness_score(row) -> int:
    """Score simples de prontidão para MVP demonstrador."""
    cooper = normalize(row.get("cooper_m_teste", row.get("cooper_m", 2600)), 2200, 3200)
    sleep = normalize(row.get("sono_h", 6.5), 5.0, 8.0)
    fatigue = normalize(row.get("fadiga", 5), 1, 10, inverse=True)
    pain = normalize(row.get("dor_muscular", 3), 0, 10, inverse=True)
    resting_hr = normalize(row.get("fc_repouso_ult", row.get("fc_repouso", 60)), 48, 75, inverse=True)
    load = normalize(row.get("carga_treino_ua", 70), 30, 120, inverse=True)

    score = (
        cooper * 0.30
        + sleep * 0.18
        + fatigue * 0.20
        + pain * 0.15
        + resting_hr * 0.10
        + load * 0.07
    )
    return int(round(clamp(score)))


def injury_risk(row) -> int:
    """Score simples de risco de lesão para MVP demonstrador."""
    fatigue = normalize(row.get("fadiga", 5), 1, 10)
    pain = normalize(row.get("dor_muscular", 3), 0, 10)
    load = normalize(row.get("carga_treino_ua", 70), 30, 130)
    sleep_risk = normalize(row.get("sono_h", 6.5), 5.0, 8.0, inverse=True)
    hr_risk = normalize(row.get("fc_repouso_ult", row.get("fc_repouso", 60)), 48, 78)
    previous_injury = 18 if str(row.get("historico_lesao", "Não")).lower() != "não" else 0

    score = fatigue * 0.25 + pain * 0.25 + load * 0.22 + sleep_risk * 0.15 + hr_risk * 0.08 + previous_injury
    return int(round(clamp(score)))


def readiness_label(score: int) -> str:
    if score >= 75:
        return "Pronto"
    if score >= 55:
        return "Atenção"
    return "Risco"


def risk_label(score: int) -> str:
    if score >= 65:
        return "Alto"
    if score >= 40:
        return "Médio"
    return "Baixo"


def add_scores(snapshot: pd.DataFrame) -> pd.DataFrame:
    df = snapshot.copy()
    df["prontidao"] = df.apply(readiness_score, axis=1)
    df["risco_lesao"] = df.apply(injury_risk, axis=1)
    df["estado_twin"] = df["prontidao"].apply(readiness_label)
    df["nivel_risco"] = df["risco_lesao"].apply(risk_label)
    return df


def generate_recommendation(row) -> str:
    readiness = row.get("prontidao", readiness_score(row))
    risk = row.get("risco_lesao", injury_risk(row))
    fatigue = row.get("fadiga", 5)
    pain = row.get("dor_muscular", 3)
    sleep = row.get("sono_h", 6.5)

    if risk >= 70 or pain >= 6:
        return "Reduzir carga e priorizar recuperação / avaliação técnica."
    if readiness < 55 or fatigue >= 7:
        return "Treino leve ou recuperação ativa; evitar intensidade alta."
    if sleep < 6:
        return "Manter treino moderado e reforçar sono/recuperação."
    if readiness >= 75 and risk < 40:
        return "Apto para treino intenso controlado."
    return "Manter plano previsto com controlo de fadiga."


def muscular_load_from_recent(registos: pd.DataFrame, militar_id: str) -> dict:
    """Mapa simples de saturação muscular baseado nos últimos treinos."""
    recent = registos[registos["id"] == militar_id].sort_values("data").tail(7)
    total = recent["carga_treino_ua"].sum() if not recent.empty else 0
    fatigue = recent["fadiga"].mean() if not recent.empty else 4
    pain = recent["dor_muscular"].mean() if not recent.empty else 2

    base = clamp(total / 7, 0, 120)
    penalty = fatigue * 4 + pain * 3

    return {
        "Peito/Ombros": int(clamp(base * 0.45 + penalty * 0.3)),
        "Costas": int(clamp(base * 0.50 + penalty * 0.25)),
        "Core/Lombar": int(clamp(base * 0.60 + penalty * 0.45)),
        "Quadríceps": int(clamp(base * 0.85 + penalty * 0.35)),
        "Posterior": int(clamp(base * 0.75 + penalty * 0.40)),
        "Gémeos": int(clamp(base * 0.70 + penalty * 0.30)),
    }

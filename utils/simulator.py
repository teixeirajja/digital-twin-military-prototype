from utils.metrics import clamp


TRAINING_BASE_LOAD = {
    "Corrida contínua": 1.00,
    "Intervalos / séries": 1.35,
    "Força - superior": 0.85,
    "Força - inferior": 1.10,
    "Marcha com carga": 1.25,
    "Recuperação ativa": 0.45,
}

MUSCLE_IMPACT = {
    "Corrida contínua": ["Quadríceps", "Posterior", "Gémeos"],
    "Intervalos / séries": ["Quadríceps", "Posterior", "Gémeos", "Core/Lombar"],
    "Força - superior": ["Peito/Ombros", "Costas", "Core/Lombar"],
    "Força - inferior": ["Quadríceps", "Posterior", "Gémeos", "Core/Lombar"],
    "Marcha com carga": ["Quadríceps", "Posterior", "Gémeos", "Core/Lombar", "Costas"],
    "Recuperação ativa": ["Quadríceps", "Posterior", "Gémeos"],
}


def simulate_training(current_readiness, current_risk, training_type, duration_min, intensity, current_muscle_load):
    """Simulação simplificada para demonstrar valor do digital twin."""
    factor = TRAINING_BASE_LOAD.get(training_type, 1.0)
    session_load = duration_min * intensity * factor / 10

    readiness_drop = session_load * 0.55
    risk_increase = session_load * 0.70

    if training_type == "Recuperação ativa":
        readiness_after = current_readiness + 4 - session_load * 0.15
        risk_after = current_risk - 4 + session_load * 0.10
    else:
        readiness_after = current_readiness - readiness_drop
        risk_after = current_risk + risk_increase

    muscles = current_muscle_load.copy()
    affected = MUSCLE_IMPACT.get(training_type, [])
    for muscle in affected:
        muscles[muscle] = int(clamp(muscles.get(muscle, 0) + session_load * 0.9, 0, 100))

    warning = ""
    if risk_after >= 70:
        warning = "Alerta: risco previsto elevado. Recomenda-se reduzir intensidade ou trocar por recuperação."
    elif readiness_after < 55:
        warning = "Atenção: prontidão prevista baixa após o treino. Controlar carga e recuperação."
    else:
        warning = "Plano aceitável para execução, mantendo monitorização da fadiga."

    return {
        "session_load": round(session_load, 1),
        "readiness_after": int(clamp(round(readiness_after))),
        "risk_after": int(clamp(round(risk_after))),
        "muscle_load_after": muscles,
        "warning": warning,
    }

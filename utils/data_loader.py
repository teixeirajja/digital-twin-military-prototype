from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@st.cache_data(show_spinner=False)
def load_data():
    """Carrega os ficheiros CSV do protótipo."""
    militares = pd.read_csv(DATA_DIR / "militares.csv")
    registos = pd.read_csv(DATA_DIR / "registos_diarios.csv", parse_dates=["data"])
    testes = pd.read_csv(DATA_DIR / "testes_fisicos.csv", parse_dates=["data"])
    lesoes = pd.read_csv(DATA_DIR / "lesoes.csv", parse_dates=["data"])
    return militares, registos, testes, lesoes


def latest_by_id(df: pd.DataFrame, date_col: str = "data") -> pd.DataFrame:
    """Devolve a última linha disponível por militar."""
    if df.empty:
        return df
    return df.sort_values(date_col).groupby("id", as_index=False).tail(1)


def build_latest_snapshot(militares: pd.DataFrame, registos: pd.DataFrame, testes: pd.DataFrame) -> pd.DataFrame:
    """Junta dados estáticos, último registo diário e último teste físico."""
    latest_reg = latest_by_id(registos).drop(columns=["tipo_treino"], errors="ignore")
    latest_test = latest_by_id(testes)
    latest_test = latest_test.rename(columns={"data": "data_teste"})
    latest_reg = latest_reg.rename(columns={"data": "data_registo"})

    base = militares.merge(latest_reg, on="id", how="left", suffixes=("", "_ult"))
    base = base.merge(latest_test, on="id", how="left", suffixes=("", "_teste"))
    return base

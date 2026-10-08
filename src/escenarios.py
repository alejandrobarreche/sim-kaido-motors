"""Supuestos de los tres escenarios de A013 y su traducción a la demanda.

Cada suceso de la tabla 4 del enunciado entra por un solo sitio: la confianza del
consumidor y los sucesos del modelo de mercado, la cuota de Kaido, el turismo (canal
de alquiladores), los coches que llegan (suministro) o el beneficio por coche (prima
de CO2). Los escenarios no tienen probabilidades asignadas.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src import demanda
from src.datos import SEGMENTOS

ESCENARIOS = ["pesimista", "central", "optimista"]  # orden de la tabla 5
MESES = 12
MESES_SIN_DATO_ECONOMICO = 9  # abril–diciembre dependen de la confianza supuesta
SEGMENTOS_CON_CODIGOS_NUEVOS = ["B", "SSUV", "CSUV", "MSUV"]
SEGMENTO_LANZAMIENTO_RETRASADO = "MSUV"  # el mayor segmento con códigos nuevos
SEGMENTO_SUMINISTRO = "MSUV"
MES_SUMINISTRO_PERDIDO = 5  # junio: índice 0 = enero


def cambios_confianza(datos: dict[str, pd.DataFrame]) -> pd.Series:
    """Variación de la confianza a nueve meses vista en todo el historial."""
    confianza = datos["economia"].set_index("t")["confianza_consumidor"]
    return (confianza.shift(-MESES_SIN_DATO_ECONOMICO) - confianza).dropna()


def efecto_renovacion(
    datos: dict[str, pd.DataFrame], serie: pd.DataFrame, meses: int = 6
) -> pd.DataFrame:
    """Cambio del logaritmo de la cuota tras cada renovación de gama.

    Compara los `meses` posteriores con los anteriores. Une renovaciones separadas por
    tres meses o menos y descarta las que se solapan con compras adelantadas o con
    el inicio y el final de los datos. CSUV no tiene historia.
    """
    renovacion = (
        datos["ventas"].groupby(["segmento", "t"])["renovacion_gama"].max().unstack(0)
    )
    marcados = (
        datos["economia"].set_index("t")[["adelanto_compras", "caida_tras_adelanto"]]
        .max(axis=1)
    )
    filas = []
    for segmento in SEGMENTOS:
        if segmento == "CSUV":
            continue
        s = serie[serie["segmento"] == segmento].set_index("t")
        anterior = None
        for t in renovacion.index[renovacion[segmento] > 0]:
            fusionada = anterior is not None and t - anterior <= 3
            anterior = t
            antes, despues = list(range(t - meses, t)), list(range(t, t + meses))
            if fusionada or min(antes) < 25 or max(despues) > demanda.T_FIN_DATOS:
                continue
            if any(marcados.get(m, 0) for m in antes + despues):
                continue
            cuota_antes = (
                s.loc[antes, "matriculaciones"].sum() / s.loc[antes, "mercado"].sum()
            )
            cuota_despues = (
                s.loc[despues, "matriculaciones"].sum()
                / s.loc[despues, "mercado"].sum()
            )
            if cuota_antes > 0 and cuota_despues > 0:
                filas.append(
                    {"segmento": segmento, "t": t,
                     "cambio_log_cuota": np.log(cuota_despues / cuota_antes)}
                )
    return pd.DataFrame(filas)


def sensibilidad_alquiladores(datos: dict[str, pd.DataFrame]) -> tuple[float, float]:
    """Pendiente del cambio interanual (log) del mercado de alquiladores sobre
    `viajeros_var` y desviación típica de `viajeros_var` (puntos porcentuales)."""
    mercado = datos["mercado"]
    alquiladores = (
        mercado[mercado["canal"] == "ALQUILADORES"].groupby("t")["unidades"].sum()
    )
    cambio = np.log(alquiladores.where(alquiladores > 0)).diff(12)
    viajeros = datos["economia"].set_index("t")["viajeros_var"]
    tabla = pd.concat([cambio, viajeros], axis=1, keys=["cambio", "viajeros"]).dropna()
    ajuste = sm.OLS(tabla["cambio"], sm.add_constant(tabla["viajeros"])).fit()
    return float(ajuste.params["viajeros"]), float(viajeros.std())


def cuota_alquiladores(datos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Peso del canal de alquiladores en las ventas de cada mes del año y segmento
    (media de A011 y A012); índice 0 = enero."""
    ventas = datos["ventas"]
    ventas = ventas[ventas["anio"].isin(["A011", "A012"])]
    total = ventas.groupby(["mes", "segmento"])["unidades"].sum()
    alquiladores = (
        ventas[ventas["canal"] == "ALQUILADORES"]
        .groupby(["mes", "segmento"])["unidades"]
        .sum()
    )
    peso = (alquiladores / total).unstack("segmento")
    peso = peso.reindex(columns=SEGMENTOS).fillna(0.0)
    return peso.reset_index(drop=True)


def definir_escenarios(
    cambio_confianza: dict[str, float],
    efecto_codigos: float,
    efecto_turismo: float,
    meses_caida: dict[str, int],
    meses_plan_ayuda: int,
    confianza_base: float,
) -> dict[str, dict]:
    """Parámetros de cada escenario (tabla 4 del enunciado).

    `cambio_confianza` da el cambio de confianza respecto al valor de diciembre de
    A012 (`confianza_base`); `efecto_codigos` es la variación relativa de la cuota por
    renovación de gama (un lanzamiento retrasado la pierde durante tres meses y unos
    códigos que se venden mejor la ganan todo el año); `efecto_turismo` es la
    variación relativa de la demanda de alquiladores; `meses_plan_ayuda` son los
    meses de plan público, que empieza en abril.
    """
    cuota = {
        nombre: pd.DataFrame(1.0, index=range(MESES), columns=SEGMENTOS)
        for nombre in ESCENARIOS
    }
    cuota["pesimista"].loc[:2, SEGMENTO_LANZAMIENTO_RETRASADO] = 1 - efecto_codigos
    cuota["optimista"][SEGMENTOS_CON_CODIGOS_NUEVOS] = 1 + efecto_codigos

    escenarios = {}
    for nombre in ESCENARIOS:
        caida = [1] * meses_caida[nombre] + [0] * (MESES - meses_caida[nombre])
        ayuda = [0] * MESES
        if nombre == "optimista":
            ayuda = [0] * (MESES - meses_plan_ayuda) + [1] * meses_plan_ayuda
        escenarios[nombre] = {
            "confianza": confianza_base + cambio_confianza[nombre],
            "eventos": {"caida_tras_adelanto": caida, "incentivo_publico": ayuda},
            "cuota": cuota[nombre],
            "turismo": {"pesimista": -efecto_turismo, "central": 0.0,
                        "optimista": efecto_turismo}[nombre],
            "llegada_perdida": (
                (SEGMENTO_SUMINISTRO, MES_SUMINISTRO_PERDIDO)
                if nombre == "pesimista" else None
            ),
            "prima_co2": nombre == "pesimista",
        }
    return escenarios


def demanda_escenario(
    datos: dict[str, pd.DataFrame],
    matrices: dict[str, pd.DataFrame],
    escenario: dict,
    peso_alquiladores: pd.DataFrame,
) -> pd.DataFrame:
    """Demanda mensual de A013 (`mes 0..11 × segmento`) de un escenario."""
    prevision = demanda.prever_demanda(
        datos, matrices, demanda.T_FIN_DATOS,
        eventos_a013=escenario["eventos"], confianza_a013=escenario["confianza"],
    )["demanda"].reset_index(drop=True)
    efecto_turismo = 1 + peso_alquiladores * escenario["turismo"]
    return prevision * escenario["cuota"] * efecto_turismo
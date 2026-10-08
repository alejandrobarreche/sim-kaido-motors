"""Previsión de la demanda mensual de Kaido por segmento.

Demanda de Kaido = mercado del segmento × cuota de Kaido. El mercado se prevé con la
variación interanual del logaritmo, que elimina la estacionalidad sin estimarla; la
cuota es la media reciente. Todas las funciones trabajan con tablas `t × segmento`
(`t` es el mes consecutivo del caso: A001-01 es 1, A012-12 es 144, A013-12 es 156)
y suponen que el código se ejecuta desde la raíz del repositorio.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.datos import SEGMENTOS, SUCESOS

T_FIN_DATOS = 144  # A012-12, último mes observado
T_FIN_A011 = 132
HORIZONTE = 12
RETRASO_ECONOMIA = 3  # meses entre la fecha del dato y el mes que explica
T_PRIMERA_VENTA = 25  # A003-01, primer mes de los datos de ventas
VARIABLE_ECONOMICA = "confianza_consumidor"
VENTANA_CUOTA = 12
# Con menos mercado en el mes base la variación interanual es solo ruido de recuento.
MERCADO_MINIMO = 200

VARIABLES_MODELO = [
    "dias_laborables_log",
    "semana_santa",
    *SUCESOS,
    "confianza_retrasada",
    "crecimiento_previo",
]

# Escenario central (tabla 4): la caída tras el adelanto dura tres meses.
EVENTOS_CENTRAL = {"caida_tras_adelanto": [1, 1, 1] + [0] * 9}


def mercado_por_segmento(datos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Mercado mensual (coches) de cada segmento, suma de los tres canales."""
    mercado = datos["mercado"].groupby(["t", "segmento"])["unidades"].sum()
    return mercado.unstack("segmento")[SEGMENTOS]


def matrices_serie(serie: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Pasa la serie de `datos.serie_mensual_segmento` a tablas `t × segmento`."""
    def pivotar(columna):
        tabla = serie.pivot_table(
            index="t", columns="segmento", values=columna, observed=True
        )
        return tabla[SEGMENTOS]

    return {
        "demanda": pivotar("demanda_observada"),
        "mercado": pivotar("mercado"),
        "en_venta": pivotar("en_venta"),
        # Sin datos de stock (antes de A009) no hay señal: se trata como 0.
        "falta_stock": pivotar("senal_falta_stock").fillna(0),
    }


def variables_exogenas(
    datos: dict[str, pd.DataFrame],
    origen: int,
    eventos_a013: dict[str, list[int]] | None = None,
    economia_real: bool = False,
    confianza_a013: float | None = None,
) -> pd.DataFrame:
    """Calendario, sucesos y economía por mes (`t` 1..156).

    Los sucesos y el calendario de los meses previstos se toman como conocidos: en
    A012 son los reales y en A013 los de `eventos_a013`. La economía entra con
    retraso: la del mes `t` es la del mes `t - 3`. Si ese dato es posterior al
    `origen` (o a A012-12 en la previsión real), se mantiene el último conocido; con
    `economia_real=True` se usa el dato real aunque no estuviera disponible en
    `origen`, lo que mide el modelo condicionado a conocer esas variables.
    `confianza_a013` sustituye ese último valor conocido en los meses sin dato.
    """
    eco = datos["economia"].set_index("t")
    cal = datos["calendario"].set_index("t")
    meses = pd.RangeIndex(1, T_FIN_DATOS + HORIZONTE + 1, name="t")

    tabla = pd.DataFrame(index=meses)
    dias = pd.concat([eco["dias_laborables"], cal["dias_laborables"]])
    tabla["dias_laborables_log"] = np.log(dias.reindex(meses))
    tabla["semana_santa"] = pd.concat([eco["semana_santa"], cal["semana_santa"]])
    for suceso in SUCESOS:
        tabla[suceso] = eco[suceso].reindex(meses)
        tabla.loc[T_FIN_DATOS + 1 :, suceso] = 0
    for suceso, valores in (eventos_a013 or {}).items():
        tabla.loc[T_FIN_DATOS + 1 : T_FIN_DATOS + len(valores), suceso] = valores

    ultimo = T_FIN_DATOS if economia_real else min(origen, T_FIN_DATOS)
    fuente = np.clip(meses - RETRASO_ECONOMIA, None, ultimo)
    valores = eco[VARIABLE_ECONOMICA].reindex(fuente)
    valores[fuente < 1] = np.nan
    tabla["confianza_retrasada"] = valores.to_numpy()
    if confianza_a013 is not None:
        tabla.loc[meses - RETRASO_ECONOMIA > ultimo, "confianza_retrasada"] = (
            confianza_a013
        )
    return tabla


def _tabla_regresion(mercado: pd.DataFrame, exogenas: pd.DataFrame) -> pd.DataFrame:
    """Apila los segmentos con la variación interanual de cada variable.

    `crecimiento_previo` es la variación interanual de hace doce meses: la inercia
    de cada segmento, conocida al decidir para todo el horizonte de previsión.
    """
    cambios = exogenas.drop(columns="crecimiento_previo", errors="ignore").diff(12)
    filas = []
    for segmento in SEGMENTOS:
        nivel = mercado[segmento].reindex(exogenas.index)
        log_nivel = np.log(nivel.where(nivel > 0))
        fila = cambios.copy()
        fila["variacion"] = log_nivel.diff(12)
        fila["crecimiento_previo"] = fila["variacion"].shift(12)
        fila["log_base"] = log_nivel.shift(12)
        fila["mercado_base"] = nivel.shift(12)
        fila["segmento"] = segmento
        filas.append(fila)
    return pd.concat(filas)


def ajustar_mercado(mercado: pd.DataFrame, exogenas: pd.DataFrame, origen: int):
    """Ajusta un modelo común a los siete segmentos con datos hasta `origen`.

    Regresión por mínimos cuadrados ponderados (peso: raíz del mercado base) de la
    variación interanual del logaritmo del mercado. No lleva constante: con ella la
    previsión arrastra el crecimiento medio de la recuperación de A005-A011, que
    sobrestima años de caída como A012. Un suceso que no aparece en el periodo de
    entrenamiento no tiene coeficiente: se omite y su efecto previsto es nulo. Los
    errores típicos que devuelve statsmodels son optimistas, porque los meses
    consecutivos están correlacionados.
    """
    tabla = _tabla_regresion(mercado, exogenas)
    entrenamiento = tabla[(tabla.index <= origen) & (tabla.index > 24)]
    entrenamiento = entrenamiento[
        entrenamiento["mercado_base"] >= MERCADO_MINIMO
    ].dropna(subset=[*VARIABLES_MODELO, "variacion"])
    variables = [v for v in VARIABLES_MODELO if entrenamiento[v].abs().sum() > 0]
    return sm.WLS(
        entrenamiento["variacion"],
        entrenamiento[variables],
        weights=np.sqrt(entrenamiento["mercado_base"]),
    ).fit()


def prever_mercado(
    modelo, mercado: pd.DataFrame, exogenas: pd.DataFrame, origen: int
) -> pd.DataFrame:
    """Mercado previsto (coches) de los doce meses siguientes a `origen`."""
    tabla = _tabla_regresion(mercado, exogenas)
    futuro = tabla[(tabla.index > origen) & (tabla.index <= origen + HORIZONTE)]
    log_prevision = futuro["log_base"] + modelo.predict(futuro[modelo.params.index])
    prevision = np.exp(log_prevision).reset_index()
    prevision["segmento"] = futuro["segmento"].to_numpy()
    return prevision.pivot(index="t", columns="segmento", values=0)[SEGMENTOS]


def cuota_reciente(
    matrices: dict[str, pd.DataFrame],
    marcados: pd.DataFrame,
    origen: int,
    ventana: int = VENTANA_CUOTA,
    minimo_meses: int = 2,
) -> pd.Series:
    """Cuota de Kaido: demanda / mercado acumulados en los últimos `ventana` meses.

    Excluye los meses marcados de cada segmento (`marcados`, `t × segmento`) y, en un
    segmento lanzado después de A003-01, su primer mes de venta, que es parcial. Si
    quedan menos de `minimo_meses`, usa la ventana sin exclusiones.
    """
    demanda, mercado = matrices["demanda"], matrices["mercado"]
    en_venta = matrices["en_venta"]
    meses = np.arange(origen - ventana + 1, origen + 1)
    cuotas = {}
    for segmento in SEGMENTOS:
        primer_mes = en_venta[segmento].idxmax()
        validos = (en_venta[segmento].loc[meses] == 1) & ~marcados.loc[meses, segmento]
        if primer_mes > T_PRIMERA_VENTA:
            validos &= meses != primer_mes
        elegidos = meses[validos.to_numpy()]
        if len(elegidos) < minimo_meses:
            elegidos = meses[(en_venta[segmento].loc[meses] == 1).to_numpy()]
        # Sin meses de venta (CSUV antes de su lanzamiento) no hay cuota.
        cuotas[segmento] = (
            demanda.loc[elegidos, segmento].sum()
            / mercado.loc[elegidos, segmento].sum()
            if len(elegidos)
            else np.nan
        )
    return pd.Series(cuotas, name="cuota")


def prever_demanda(
    datos: dict[str, pd.DataFrame],
    matrices: dict[str, pd.DataFrame],
    origen: int,
    eventos_a013: dict[str, list[int]] | None = None,
    economia_real: bool = False,
    confianza_a013: float | None = None,
    excluir_falta_stock: bool = False,
) -> dict[str, pd.DataFrame | pd.Series | object]:
    """Previsión de los doce meses siguientes a `origen`, con datos hasta `origen`.

    Devuelve el mercado y la demanda previstos (`t × segmento`), la cuota usada y el
    modelo ajustado. Para `origen` = A012-12 es la previsión de A013. La cuota excluye
    siempre los meses de compras adelantadas y su caída, y con `excluir_falta_stock`
    también los meses con señal de falta de stock.
    """
    exogenas = variables_exogenas(
        datos, origen, eventos_a013, economia_real, confianza_a013
    )
    mercado = matrices["mercado"].loc[:origen]
    modelo = ajustar_mercado(mercado, exogenas, origen)
    mercado_prev = prever_mercado(modelo, mercado, exogenas, origen)
    suceso = datos["economia"].set_index("t")[
        ["adelanto_compras", "caida_tras_adelanto"]
    ].max(axis=1)
    marcados = pd.DataFrame(
        {s: suceso.astype(bool) for s in SEGMENTOS}, index=suceso.index
    )
    if excluir_falta_stock:
        falta = matrices["falta_stock"].astype(bool)
        marcados |= falta.reindex(marcados.index, fill_value=False)
    cuota = cuota_reciente(matrices, marcados, origen)
    return {
        "modelo": modelo,
        "mercado": mercado_prev,
        "cuota": cuota,
        "demanda": mercado_prev * cuota,
    }


def referencia_estacional(demanda: pd.DataFrame, origen: int) -> pd.DataFrame:
    """Demanda del mismo mes del año anterior, como referencia sin modelo."""
    referencia = demanda.loc[origen - HORIZONTE + 1 : origen].copy()
    referencia.index = referencia.index + HORIZONTE
    return referencia


def metricas(
    prevision: pd.DataFrame, observado: pd.DataFrame, segmentos: list[str]
) -> pd.DataFrame:
    """MAE y sesgo por segmento y total, con error = previsión − observado.

    Las medidas absolutas son coches por mes; las relativas, sobre la media mensual
    observada. El total suma los segmentos indicados antes de calcular el error.
    """
    prevision = prevision[segmentos]
    observado = observado.loc[prevision.index, segmentos]
    prevision = prevision.assign(Total=prevision.sum(axis=1))
    observado = observado.assign(Total=observado.sum(axis=1))
    error = prevision - observado
    resultado = pd.DataFrame(
        {
            "observado_medio": observado.mean(),
            "mae": error.abs().mean(),
            "sesgo": error.mean(),
        }
    )
    resultado["mae_pct"] = resultado["mae"] / resultado["observado_medio"]
    resultado["sesgo_pct"] = resultado["sesgo"] / resultado["observado_medio"]
    resultado.index.name = "segmento"
    return resultado.reset_index()
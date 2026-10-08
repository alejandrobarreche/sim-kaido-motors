"""Simulación mensual de un año de la cadena de suministro de Kaido.

Cada segmento se simula por separado, con meses `0..11` (enero–diciembre de A013).
Las llegadas `L` son los coches que se facturan a la red en el mes; las ventas son a
clientes (la demanda de `demanda.py`, sin automatriculaciones). El stock se lleva por
cohortes de entrada y se vende primero el más antiguo (FIFO).

Aproximaciones de tiempo, todas en días de un año de 365:
- las llegadas entran el día 15 de su mes (mitad del mes) y las ventas de un mes se
  reparten por igual, de modo que se producen de media a mitad de mes;
- el stock inicial se reparte por igual dentro de cada tramo de antigüedad en bloques
  de 30 días; los coches con más de 180 días se tratan como un solo bloque.
"""

import numpy as np
import pandas as pd

from src.datos import SEGMENTOS

DIAS_MES = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
INICIO_MES = np.concatenate([[0], DIAS_MES.cumsum()[:-1]])
MITAD_MES = INICIO_MES + DIAS_MES / 2
FIN_MES = INICIO_MES + DIAS_MES

COSTE_DIA_STOCK = 2.0  # €/coche/día para la marca
LIMITE_COSTE_DIAS = 180  # antigüedad total máxima que genera coste
PCT_TRANSFER = 0.20  # del beneficio bruto del coche
PLAZO_MESES = 3  # la decisión de hoy llega dentro de tres meses
Z_DEFECTO = 1.28  # cubre nueve de cada diez meses
MESES_REFERENCIA_LLEGADAS = 6  # meses de A012 que fijan las llegadas ya en camino

# Edad (días) a 31 de diciembre de cada bloque de 30 días del stock inicial.
EDADES_0_90 = (15, 45, 75)
EDADES_91_180 = (105, 135, 165)
EDAD_MAS_180 = 210  # solo importa que supere 180


def economia_segmentos(datos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Beneficio bruto y VM por tramo de antigüedad de cada segmento (€/coche).

    El beneficio bruto es el de la tarifa de A013 sin prima de CO2; el VM es el real
    de A011–A012 según los días que pasó el coche en la red.
    """
    columnas = {
        "beneficio_bruto_marca_eur": "bruto",
        "vm_real_0_90_eur": "vm_0_90",
        "vm_real_91_180_eur": "vm_91_180",
        "vm_real_mas_180_eur": "vm_mas_180",
    }
    ficha = datos["segmentos"].set_index("segmento")[list(columnas)]
    return ficha.rename(columns=columnas).reindex(SEGMENTOS)


def stock_inicial(datos: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Cohortes del stock a fin de A012; `entrada` son días desde el 1 de enero."""
    stock = datos["stock"].loc[datos["stock"]["periodo"] == "A0121201"]
    stock = stock.set_index("segmento")
    cohortes = {}
    for segmento in SEGMENTOS:
        fila = stock.loc[segmento]
        edades = [*EDADES_0_90, *EDADES_91_180, EDAD_MAS_180]
        unidades = (
            [fila["s_0_90"] / 3] * 3 + [fila["s_91_180"] / 3] * 3 + [fila["s_mas_180"]]
        )
        cohortes[segmento] = pd.DataFrame(
            {"entrada": [-edad for edad in edades], "unidades": unidades}
        )
    return cohortes


def llegadas_iniciales(
    datos: dict[str, pd.DataFrame],
    meses: int = MESES_REFERENCIA_LLEGADAS,
    multiplicador: float = 1.0,
) -> pd.DataFrame:
    """Llegadas de enero y febrero de A013, ya en camino al empezar el año.

    Se suponen iguales a la media mensual de la facturación a la red (`wholesale`) de
    los últimos `meses` de A012, desde el primer mes con facturación del segmento
    (CSUV empieza en agosto), redondeada a coches enteros. `multiplicador` permite
    probar si la cifra supuesta es alta o baja.
    """
    stock = datos["stock"]
    reciente = stock[stock["t"] > stock["t"].max() - meses]
    tabla = reciente.pivot(index="t", columns="segmento", values="wholesale")
    medias = {}
    for segmento in SEGMENTOS:
        serie = tabla[segmento]
        medias[segmento] = serie[serie.cumsum() > 0].mean()
    llegadas = np.round(pd.Series(medias) * multiplicador)
    return pd.DataFrame([llegadas, llegadas], index=[0, 1])[SEGMENTOS]


def stock_seguridad(sigma: pd.DataFrame, z: float = Z_DEFECTO) -> pd.DataFrame:
    """SS = z · σ · √3, con σ el error típico mensual de la previsión (coches)."""
    return z * sigma * np.sqrt(PLAZO_MESES)


def llegada_a_pedir(
    stock_proyectado: float, demanda_prevista: float, stock_seg: float
) -> int:
    """Llegada del mes t+3: lo que falta para cubrir la demanda y el stock de seguridad.

    Se redondea hacia arriba a coches enteros para no quedar por debajo del objetivo.
    """
    return int(np.ceil(max(0.0, demanda_prevista + stock_seg - stock_proyectado)))


def planificar_llegadas(
    demanda_prevista: pd.DataFrame,
    stock_a_fin_de_ano: pd.Series,
    llegadas_en_camino: pd.DataFrame,
    stock_seg: pd.DataFrame,
) -> pd.DataFrame:
    """Plan de llegadas de A013 decidido a fin de A012 con la demanda prevista.

    Enero y febrero son las llegadas en camino. Para cada mes posterior se proyecta el
    stock hasta el mes anterior (sin bajar de cero) y se aplica `llegada_a_pedir`. Con
    la demanda igual a la prevista, revisar cada mes no cambia este plan.
    """
    plan = pd.DataFrame(0, index=demanda_prevista.index, columns=SEGMENTOS)
    for segmento in SEGMENTOS:
        proyectado = float(stock_a_fin_de_ano[segmento])
        for mes in demanda_prevista.index:
            if mes < PLAZO_MESES - 1:
                llegada = int(llegadas_en_camino.loc[mes, segmento])
            else:
                llegada = llegada_a_pedir(
                    proyectado,
                    demanda_prevista.loc[mes, segmento],
                    stock_seg.loc[mes, segmento],
                )
            plan.loc[mes, segmento] = llegada
            proyectado = max(
                0.0, proyectado + llegada - demanda_prevista.loc[mes, segmento]
            )
    return plan


def _coste_dias(entrada: np.ndarray, desde: float, hasta: np.ndarray) -> np.ndarray:
    """Coste (€/coche) entre dos días, sin pasar de 180 días de antigüedad total."""
    inicio = np.maximum(entrada, desde)
    edad_ini = np.minimum(inicio - entrada, LIMITE_COSTE_DIAS)
    edad_fin = np.minimum(hasta - entrada, LIMITE_COSTE_DIAS)
    return COSTE_DIA_STOCK * np.maximum(edad_fin - edad_ini, 0.0)


def _vm_por_edad(edad: np.ndarray, economia: pd.Series) -> np.ndarray:
    return np.select(
        [edad <= 90, edad <= 180],
        [economia["vm_0_90"], economia["vm_91_180"]],
        default=economia["vm_mas_180"],
    )


def simular_segmento(
    segmento: str,
    demanda: pd.Series,
    llegadas: pd.Series,
    cohortes: pd.DataFrame,
    economia: pd.Series,
) -> pd.DataFrame:
    """Simula un año de un segmento y devuelve una fila por mes.

    `V = min(D, S + L)`; lo que no se puede servir son ventas perdidas (no hay
    transfers en esta versión). El coste del stock es el de la marca: 2 €/coche/día
    mientras el coche lleva menos de 180 días facturado, incluidos los días de A012 de
    los coches que ya estaban en la red. No incluye los intereses del concesionario.
    """
    entrada = cohortes["entrada"].to_numpy(dtype=float)
    unidades = cohortes["unidades"].to_numpy(dtype=float)
    filas = []
    for mes in range(len(DIAS_MES)):
        entrada = np.append(entrada, MITAD_MES[mes])
        unidades = np.append(unidades, float(llegadas.iloc[mes]))
        orden = np.argsort(entrada, kind="stable")
        entrada, unidades = entrada[orden], unidades[orden]

        stock_ini = unidades.sum() - llegadas.iloc[mes]
        vendidos = min(float(demanda.iloc[mes]), unidades.sum())
        # FIFO: lo vendido sale de las cohortes más antiguas.
        acumulado = np.cumsum(unidades)
        salen = np.clip(vendidos - (acumulado - unidades), 0.0, unidades)
        quedan = unidades - salen

        edad_venta = MITAD_MES[mes] - entrada
        vm = (salen * _vm_por_edad(edad_venta, economia)).sum()
        coste = (
            salen * _coste_dias(entrada, INICIO_MES[mes], MITAD_MES[mes])
            + quedan * _coste_dias(entrada, INICIO_MES[mes], FIN_MES[mes])
        ).sum()

        edad_fin = FIN_MES[mes] - entrada
        filas.append(
            {
                "segmento": segmento,
                "mes": mes + 1,
                "stock_inicial": stock_ini,
                "llegadas": float(llegadas.iloc[mes]),
                "demanda": float(demanda.iloc[mes]),
                "ventas": vendidos,
                "perdidas": float(demanda.iloc[mes]) - vendidos,
                "stock_fin": quedan.sum(),
                "stock_0_90": quedan[edad_fin <= 90].sum(),
                "stock_91_180": quedan[(edad_fin > 90) & (edad_fin <= 180)].sum(),
                "stock_mas_180": quedan[edad_fin > 180].sum(),
                "beneficio_bruto": vendidos * economia["bruto"],
                "vm": vm,
                "coste_stock": coste,
            }
        )
        entrada, unidades = entrada[quedan > 1e-9], quedan[quedan > 1e-9]
    resultado = pd.DataFrame(filas)
    resultado["cvp"] = resultado["beneficio_bruto"] - resultado["vm"]
    resultado["cvp_perdido"] = resultado["perdidas"] * (
        economia["bruto"] - economia["vm_0_90"]
    )
    resultado["coste_transfer_alternativo"] = (
        resultado["perdidas"] * PCT_TRANSFER * economia["bruto"]
    )
    return resultado


def simular_anio(
    demanda: pd.DataFrame,
    llegadas: pd.DataFrame,
    cohortes: dict[str, pd.DataFrame],
    economia: pd.DataFrame,
) -> pd.DataFrame:
    """Simula los siete segmentos; `demanda` y `llegadas` son `mes × segmento`."""
    return pd.concat(
        [
            simular_segmento(s, demanda[s], llegadas[s], cohortes[s], economia.loc[s])
            for s in SEGMENTOS
        ],
        ignore_index=True,
    )


def comprobar_balance(
    mensual: pd.DataFrame, cohortes: dict[str, pd.DataFrame], tolerancia: float = 1e-6
) -> pd.DataFrame:
    """Comprueba el balance de unidades de cada segmento; una fila por comprobación.

    Cubre `S_fin = S_ini + L − V`, la continuidad de un mes al siguiente, la suma de
    los tramos de antigüedad, `V + perdidas = D`, `V ≤ S + L` y la ausencia de stock
    negativo.
    """
    filas = []
    for segmento, grupo in mensual.groupby("segmento", sort=False):
        s0 = cohortes[segmento]["unidades"].sum()
        mes_a_mes = grupo["stock_fin"] - (
            grupo["stock_inicial"] + grupo["llegadas"] - grupo["ventas"]
        )
        continuidad = grupo["stock_inicial"].iloc[1:].to_numpy() - grupo[
            "stock_fin"
        ].iloc[:-1].to_numpy()
        tramos = (
            grupo[["stock_0_90", "stock_91_180", "stock_mas_180"]].sum(axis=1)
            - grupo["stock_fin"]
        )
        anual = (
            s0
            + grupo["llegadas"].sum()
            - grupo["ventas"].sum()
            - grupo["stock_fin"].iloc[-1]
        )
        filas.append(
            {
                "segmento": segmento,
                "balance_mensual": mes_a_mes.abs().max(),
                "balance_anual": abs(anual),
                "continuidad_stock": np.abs(continuidad).max(),
                "suma_tramos": tramos.abs().max(),
                "ventas_mas_perdidas_menos_demanda": (
                    grupo["ventas"] + grupo["perdidas"] - grupo["demanda"]
                ).abs().max(),
                "exceso_de_ventas": (
                    grupo["ventas"] - grupo["stock_inicial"] - grupo["llegadas"]
                ).max(),
                "stock_minimo": grupo["stock_fin"].min(),
            }
        )
    resultado = pd.DataFrame(filas)
    balances = [
        "balance_mensual",
        "balance_anual",
        "continuidad_stock",
        "suma_tramos",
        "ventas_mas_perdidas_menos_demanda",
    ]
    resultado["correcto"] = (
        (resultado[balances] < tolerancia).all(axis=1)
        & (resultado["exceso_de_ventas"] < tolerancia)
        & (resultado["stock_minimo"] > -tolerancia)
    )
    return resultado
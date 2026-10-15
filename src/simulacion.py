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

# Revisión mensual del plan: la previsión de los meses futuros se corrige con la
# razón entre las ventas y la previsión de los últimos tres meses, a medias (la
# demanda no servida no se observa) y acotada.
VENTANA_REVISION = 3
PESO_REVISION = 0.5
LIMITES_REVISION = (0.5, 1.5)

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
    economia = ficha.rename(columns=columnas).reindex(SEGMENTOS)
    # CSUV no tiene ventas con más de 180 días: se usa el VM del tramo anterior.
    economia["vm_mas_180"] = economia["vm_mas_180"].fillna(economia["vm_91_180"])
    return economia


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


def avanzar_mes(
    entrada: np.ndarray,
    unidades: np.ndarray,
    mes: int,
    llegada: float,
    demanda: float,
    economia: pd.Series,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Simula un mes de un segmento: entrada de coches, venta FIFO y costes.

    `V = min(D, S + L)`; lo que no se puede servir son ventas perdidas (no hay
    transfers en esta versión). El coste del stock es el de la marca: 2 €/coche/día
    mientras el coche lleva menos de 180 días facturado, incluidos los días de A012 de
    los coches que ya estaban en la red. No incluye los intereses del concesionario.
    Devuelve las cohortes que quedan y los results del mes.
    """
    entrada = np.append(entrada, MITAD_MES[mes])
    unidades = np.append(unidades, float(llegada))
    orden = np.argsort(entrada, kind="stable")
    entrada, unidades = entrada[orden], unidades[orden]

    stock_ini = unidades.sum() - llegada
    vendidos = min(float(demanda), unidades.sum())
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
    fila = {
        "mes": mes + 1,
        "stock_inicial": stock_ini,
        "llegadas": float(llegada),
        "demanda": float(demanda),
        "ventas": vendidos,
        "perdidas": float(demanda) - vendidos,
        "stock_fin": quedan.sum(),
        "stock_0_90": quedan[edad_fin <= 90].sum(),
        "stock_91_180": quedan[(edad_fin > 90) & (edad_fin <= 180)].sum(),
        "stock_mas_180": quedan[edad_fin > 180].sum(),
        "beneficio_bruto": vendidos * economia["bruto"],
        "vm": vm,
        "coste_stock": coste,
    }
    vivos = quedan > 1e-9
    return entrada[vivos], quedan[vivos], fila


def _derivadas(resultado: pd.DataFrame, economia: pd.Series) -> pd.DataFrame:
    """Añade CVP, CVP de las ventas perdidas y coste del transfer alternativo."""
    resultado["cvp"] = resultado["beneficio_bruto"] - resultado["vm"]
    resultado["cvp_perdido"] = resultado["perdidas"] * (
        economia["bruto"] - economia["vm_0_90"]
    )
    resultado["coste_transfer_alternativo"] = (
        resultado["perdidas"] * PCT_TRANSFER * economia["bruto"]
    )
    return resultado


def simular_segmento(
    segmento: str,
    demanda: pd.Series,
    llegadas: pd.Series,
    cohortes: pd.DataFrame,
    economia: pd.Series,
) -> pd.DataFrame:
    """Simula un año de un segmento con llegadas dadas y devuelve una fila por mes."""
    entrada = cohortes["entrada"].to_numpy(dtype=float)
    unidades = cohortes["unidades"].to_numpy(dtype=float)
    filas = []
    for mes in range(len(DIAS_MES)):
        entrada, unidades, fila = avanzar_mes(
            entrada, unidades, mes, llegadas.iloc[mes], demanda.iloc[mes], economia
        )
        filas.append({"segmento": segmento, **fila})
    return _derivadas(pd.DataFrame(filas), economia)


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
    los tramos de antigüedad, `V + perdidas = D`, `V ≤ S + L`, la ausencia de stock
    negativo y de valores ausentes (que las sumas de pandas ignorarían en silencio).
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
                "valores_ausentes": int(grupo.isna().sum().sum()),
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
        & (resultado["valores_ausentes"] == 0)
    )
    return resultado

METRICAS = [
    "demanda", "ventas", "perdidas", "llegadas", "stock_medio", "stock_fin",
    "stock_mas_90_fin", "coste_stock", "vm", "cvp", "cvp_perdido",
    "transfer_alternativo",
]


def factores_demanda(
    rng: np.random.Generator,
    n_rep: int,
    sd_relativa: np.ndarray,
    phi: float,
    rho: float,
) -> np.ndarray:
    """Errores multiplicativos de la demanda, de forma `(n_rep, 12, segmentos)`.

    `exp(σ·ε − σ²/2)` tiene media 1: la demanda real iguala a la prevista en media.
    `ε` combina un factor común a todos los segmentos (correlación `rho`) con otro
    propio, ambos AR(1) con coeficiente `phi` y varianza 1.
    """
    meses, k = len(DIAS_MES), len(sd_relativa)

    def ar1(forma):
        x = np.empty(forma)
        x[:, 0] = rng.standard_normal(forma[0:1] + forma[2:])
        for mes in range(1, meses):
            ruido = rng.standard_normal(forma[0:1] + forma[2:])
            x[:, mes] = phi * x[:, mes - 1] + np.sqrt(1 - phi**2) * ruido
        return x

    comun = ar1((n_rep, meses))
    propio = ar1((n_rep, meses, k))
    eps = np.sqrt(rho) * comun[:, :, None] + np.sqrt(1 - rho) * propio
    return np.exp(sd_relativa * eps - sd_relativa**2 / 2)


def simular_replica(
    demanda_real: np.ndarray,
    demanda_plan: np.ndarray,
    plan_inicial: np.ndarray,
    cohortes: pd.DataFrame,
    economia: pd.Series,
    sd_relativa: float,
    z: float = Z_DEFECTO,
    llegada_perdida: int | None = None,
) -> tuple[dict, np.ndarray]:
    """Un año de un segmento con revisión mensual de la llegada de t + 3.

    `demanda_plan` es la previsión central con la que se decide; `demanda_real` es la
    que ocurre. Tras cerrar cada mes se corrige la previsión con las ventas
    observadas y se recalcula solo la llegada de dentro de tres meses; lo que ya está
    en camino no se toca. `llegada_perdida` es un mes en que no llega nada (fallo de
    suministro). Devuelve los totales del año y el stock y las ventas de cada mes.
    """
    entrada = cohortes["entrada"].to_numpy(dtype=float)
    unidades = cohortes["unidades"].to_numpy(dtype=float)
    llegadas = plan_inicial.astype(float).copy()
    ventas_mes = np.zeros(len(DIAS_MES))
    mensual = np.zeros((len(DIAS_MES), 2))
    acumulado = dict.fromkeys(
        ["demanda", "ventas", "perdidas", "llegadas", "coste_stock", "vm", "cvp",
         "cvp_perdido", "transfer_alternativo"], 0.0)
    for mes in range(len(DIAS_MES)):
        llegada = 0.0 if mes == llegada_perdida else llegadas[mes]
        entrada, unidades, fila = avanzar_mes(
            entrada, unidades, mes, llegada, demanda_real[mes], economia)
        ventas_mes[mes] = fila["ventas"]
        mensual[mes] = (fila["stock_fin"], fila["ventas"])
        perdidas = fila["perdidas"]
        acumulado["demanda"] += fila["demanda"]
        acumulado["ventas"] += fila["ventas"]
        acumulado["perdidas"] += perdidas
        acumulado["llegadas"] += llegada
        acumulado["coste_stock"] += fila["coste_stock"]
        acumulado["vm"] += fila["vm"]
        acumulado["cvp"] += fila["beneficio_bruto"] - fila["vm"]
        acumulado["cvp_perdido"] += perdidas * (
            economia["bruto"] - economia["vm_0_90"]
        )
        acumulado["transfer_alternativo"] += perdidas * PCT_TRANSFER * economia["bruto"]

        destino = mes + PLAZO_MESES
        if destino < len(DIAS_MES):
            ventana = slice(max(0, mes - VENTANA_REVISION + 1), mes + 1)
            previsto = demanda_plan[ventana].sum()
            razon = ventas_mes[ventana].sum() / previsto if previsto > 0 else 1.0
            factor = np.clip(1 + PESO_REVISION * (razon - 1), *LIMITES_REVISION)
            proyectado = unidades.sum()
            for j in range(mes + 1, destino):
                esperado_j = factor * demanda_plan[j]
                proyectado = max(0.0, proyectado + llegadas[j] - esperado_j)
            esperada = factor * demanda_plan[destino]
            ss = z * sd_relativa * esperada * np.sqrt(PLAZO_MESES)
            llegadas[destino] = llegada_a_pedir(proyectado, esperada, ss)
    acumulado["stock_medio"] = mensual[:, 0].mean()
    acumulado["stock_fin"] = mensual[-1, 0]
    edad_fin = FIN_MES[-1] - entrada
    acumulado["stock_mas_90_fin"] = unidades[edad_fin > 90].sum()
    return acumulado, mensual


def simular_escenario(
    demanda_prevista: pd.DataFrame,
    demanda_plan: pd.DataFrame,
    plan_inicial: pd.DataFrame,
    factores: np.ndarray,
    cohortes: dict[str, pd.DataFrame],
    economia: pd.DataFrame,
    sd_relativa: pd.Series,
    z: float | pd.Series = Z_DEFECTO,
    llegada_perdida: tuple[str, int] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Repite el año con los errores `factores` y devuelve sus results.

    La demanda real de cada repetición es la del escenario (`demanda_prevista`) por
    el error, redondeada a coches enteros. `z` puede ser un valor común o uno por
    segmento (Series). Devuelve un array `(n_rep, segmento, METRICAS)` y otro
    `(n_rep, mes, segmento, 2)` con stock y ventas mensuales.
    """
    n_rep = factores.shape[0]
    totales = np.zeros((n_rep, len(SEGMENTOS), len(METRICAS)))
    mensual = np.zeros((n_rep, len(DIAS_MES), len(SEGMENTOS), 2))
    real = np.rint(demanda_prevista.to_numpy() * factores)
    for j, segmento in enumerate(SEGMENTOS):
        perdida = (
            llegada_perdida[1]
            if llegada_perdida is not None and llegada_perdida[0] == segmento
            else None
        )
        for r in range(n_rep):
            acumulado, mes_a_mes = simular_replica(
                real[r, :, j], demanda_plan[segmento].to_numpy(),
                plan_inicial[segmento].to_numpy(), cohortes[segmento],
                economia.loc[segmento], sd_relativa[segmento],
                float(z[segmento]) if isinstance(z, pd.Series) else z, perdida)
            totales[r, j] = [acumulado[m] for m in METRICAS]
            mensual[r, :, j] = mes_a_mes
    return totales, mensual

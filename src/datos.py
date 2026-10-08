"""Lectura, comprobación y preparación de los datos de Kaido Motors.

Todas las funciones trabajan con los CSV de `data/` como entradas de solo lectura y
suponen que el código se ejecuta desde la raíz del repositorio.
"""

from pathlib import Path

import numpy as np
import pandas as pd

RUTA_DATOS = Path("data")

SEGMENTOS = ["B", "C", "MD", "SSUV", "CSUV", "MSUV", "S"]
CANALES = ["PARTICULARES", "EMPRESAS_RENTING", "ALQUILADORES"]

ARCHIVOS = {
    "ventas": "ventas_kaido_mensuales.csv",
    "stock": "stock_red_mensual.csv",
    "mercado": "mercado_mensual.csv",
    "economia": "economia_eventos_mensuales.csv",
    "segmentos": "catalogo_segmentos.csv",
    "modelos": "catalogo_modelos.csv",
    "calendario": "calendario_mensual_a013.csv",
}

SUCESOS = ["incentivo_publico", "adelanto_compras", "caida_tras_adelanto", "subida_iva"]

# Stock libre (sin cliente) a fin de mes por debajo de media venta mensual: menos de
# unas dos semanas de coches disponibles. Corresponde aproximadamente al 5-10 % de
# meses con menor cobertura de cada segmento entre A009 y A012.
UMBRAL_STOCK_LIBRE = 0.5

# Ventas de Kaido entre A003 y A012 según el anexo 5 del enunciado.
TOTAL_VENTAS_ENUNCIADO = 125_030


def leer_csv(nombre: str, ruta: Path = RUTA_DATOS) -> pd.DataFrame:
    """Lee un CSV del caso. Solo las celdas vacías son ausentes: `NA` es un código."""
    return pd.read_csv(ruta / nombre, keep_default_na=False, na_values=[""])


def fecha_ficticia(df: pd.DataFrame) -> pd.Series:
    """Convierte `anio` (A001...) y `mes` en una fecha con año ficticio 2001...

    Solo conserva orden y distancia entre meses; el calendario laboral se toma
    siempre de los CSV, nunca de esta fecha.
    """
    anio = 2000 + df["anio"].str[1:].astype(int)
    return pd.to_datetime(pd.DataFrame({"year": anio, "month": df["mes"], "day": 1}))


def cargar_datos(ruta: Path = RUTA_DATOS) -> dict[str, pd.DataFrame]:
    """Carga los siete CSV y añade `fecha` a las tablas mensuales."""
    datos = {clave: leer_csv(nombre, ruta) for clave, nombre in ARCHIVOS.items()}
    for clave in ["ventas", "stock", "mercado", "economia", "calendario"]:
        datos[clave]["fecha"] = fecha_ficticia(datos[clave])
    return datos


def _comprobacion(nombre: str, correcto: bool, detalle: str) -> dict:
    return {"comprobacion": nombre, "correcto": bool(correcto), "detalle": detalle}


def _meses_completos(df: pd.DataFrame, claves: list[str]) -> tuple[bool, str]:
    """Comprueba que cada combinación de claves tiene todos los meses seguidos."""
    rango = df.groupby(claves)["t"].agg(["min", "max", "count", "nunique"])
    correcto = (
        (rango["count"] == rango["max"] - rango["min"] + 1)
        & (rango["count"] == rango["nunique"])
    ).all()
    detalle = f"t {df['t'].min()}-{df['t'].max()}, {len(rango)} series"
    return correcto, detalle


def comprobar_datos(datos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Comprueba claves, periodos, ausencias y coherencia entre ficheros.

    Devuelve una fila por comprobación con su resultado y un detalle cuantificado.
    El balance de stock se analiza aparte en `balance_stock`.
    """
    ventas, stock, mercado = datos["ventas"], datos["stock"], datos["mercado"]
    economia, modelos = datos["economia"], datos["modelos"]
    segmentos, calendario = datos["segmentos"], datos["calendario"]
    filas = []

    for nombre, df, claves in [
        ("ventas", ventas, ["t", "segmento", "canal"]),
        ("stock", stock, ["t", "segmento"]),
        ("mercado", mercado, ["t", "segmento", "canal"]),
        ("economia", economia, ["t"]),
    ]:
        duplicados = df.duplicated(claves).sum()
        filas.append(
            _comprobacion(
                f"Claves únicas en {nombre}", duplicados == 0, f"{duplicados} duplicados"
            )
        )
        if len(claves) > 1:
            correcto, detalle = _meses_completos(df, claves[1:])
        else:
            correcto, detalle = _meses_completos(df.assign(_=0), ["_"])
        filas.append(_comprobacion(f"Meses completos en {nombre}", correcto, detalle))

    filas.append(
        _comprobacion(
            "Segmentos y canales esperados",
            set(ventas["segmento"]) == set(SEGMENTOS)
            and set(ventas["canal"]) == set(CANALES)
            and set(mercado["canal"]) == set(CANALES),
            f"{ventas['segmento'].nunique()} segmentos, {ventas['canal'].nunique()} canales",
        )
    )
    filas.append(
        _comprobacion(
            "Calendario A013 con 12 meses (t 145-156)",
            calendario["t"].tolist() == list(range(145, 157)),
            f"{len(calendario)} meses",
        )
    )
    filas.append(
        _comprobacion(
            "Economía sin ausencias",
            economia.isna().sum().sum() == 0,
            f"{economia.isna().sum().sum()} celdas vacías",
        )
    )

    total = ventas["unidades"].sum()
    filas.append(
        _comprobacion(
            "Total de ventas A003-A012 igual al enunciado",
            total == TOTAL_VENTAS_ENUNCIADO,
            f"{total} coches",
        )
    )

    cruce = mercado.merge(
        ventas[["t", "segmento", "canal", "unidades"]],
        on=["t", "segmento", "canal"],
        suffixes=("_mercado", "_kaido"),
    )
    dif = (cruce["marca_propia"] - cruce["unidades_kaido"]).abs().max()
    filas.append(
        _comprobacion(
            "marca_propia del mercado igual a ventas de Kaido",
            dif == 0,
            f"diferencia máxima {dif} coches",
        )
    )
    excede = (cruce["unidades_kaido"] > cruce["unidades_mercado"]).sum()
    filas.append(
        _comprobacion(
            "Kaido no supera al mercado de su celda", excede == 0, f"{excede} celdas"
        )
    )

    partes = (ventas["u_automatriculacion"] > ventas["unidades"]) | (
        ventas["u_venta_especial"] > ventas["unidades"]
    )
    filas.append(
        _comprobacion(
            "Automatriculaciones y ventas especiales no superan las ventas",
            partes.sum() == 0,
            f"{partes.sum()} filas",
        )
    )

    con_edad = ventas.dropna(subset=["u_0_90"])
    dif_edad = (
        con_edad[["u_0_90", "u_91_180", "u_mas_180"]].sum(axis=1) - con_edad["unidades"]
    ).abs()
    primer_mes_edad = con_edad["periodo"].min()
    filas.append(
        _comprobacion(
            "Tramos de edad de ventas suman las ventas",
            dif_edad.max() == 0,
            f"{len(con_edad)} filas desde {primer_mes_edad}",
        )
    )
    sin_edad_tarde = ventas[(ventas["t"] >= 98) & ventas["u_0_90"].isna()]
    filas.append(
        _comprobacion(
            "Edad de ventas disponible desde A009-02",
            sin_edad_tarde.empty and primer_mes_edad == "A0090201",
            f"{len(sin_edad_tarde)} filas vacías desde A009-02",
        )
    )

    dif_stock = (
        stock[["s_0_90", "s_91_180", "s_mas_180"]].sum(axis=1) - stock["stock_total"]
    ).abs()
    filas.append(
        _comprobacion(
            "Tramos de edad del stock suman el stock",
            dif_stock.max() == 0,
            f"diferencia máxima {dif_stock.max()} coches",
        )
    )
    filas.append(
        _comprobacion(
            "Stock sin cliente no supera el stock",
            (stock["s_sin_cliente"] <= stock["stock_total"]).all(),
            f"{(stock['s_sin_cliente'] > stock['stock_total']).sum()} filas",
        )
    )
    sin_wholesale = stock.loc[stock["wholesale"].isna(), "periodo"].unique().tolist()
    filas.append(
        _comprobacion(
            "wholesale vacío solo en A009-01",
            sin_wholesale == ["A0090101"],
            f"meses vacíos: {sin_wholesale}",
        )
    )

    numericas = ["unidades", "u_automatriculacion", "u_venta_especial"]
    negativos = (ventas[numericas] < 0).sum().sum() + (
        stock[["stock_total", "wholesale"]] < 0
    ).sum().sum()
    filas.append(
        _comprobacion("Sin cantidades negativas", negativos == 0, f"{negativos} celdas")
    )

    ficha = segmentos.set_index("segmento")
    por_segmento = ventas.groupby("segmento")["unidades"].sum().reindex(ficha.index)
    a012 = (
        ventas[ventas["anio"] == "A012"]
        .groupby("segmento")["unidades"]
        .sum()
        .reindex(ficha.index)
    )
    filas.append(
        _comprobacion(
            "Ficha de segmentos coherente con ventas (total y A012)",
            (ficha["unidades_totales"] == por_segmento).all()
            and (ficha["unidades_ult_anio"] == a012).all(),
            "unidades_totales y unidades_ult_anio",
        )
    )
    filas.append(
        _comprobacion(
            "Catálogo de modelos suma las ventas de cada segmento",
            (
                modelos.groupby("segmento")["unidades"].sum().reindex(ficha.index)
                == por_segmento
            ).all(),
            f"{len(modelos)} códigos y generaciones",
        )
    )
    duplicados = modelos.duplicated(["codigo_modelo", "generacion"]).sum()
    filas.append(
        _comprobacion(
            "Código y generación identifican cada modelo",
            duplicados == 0,
            f"{duplicados} duplicados; código NA presente: "
            f"{(modelos['codigo_modelo'] == 'NA').any()}",
        )
    )
    en_tarifa = (
        modelos.groupby("segmento")["en_tarifa_A013"].sum().reindex(ficha.index)
    )
    nuevos = (
        modelos[(modelos["en_tarifa_A013"] == 1) & (modelos["unidades"] == 0)]
        .groupby("segmento")
        .size()
        .reindex(ficha.index, fill_value=0)
    )
    filas.append(
        _comprobacion(
            "Gama A013 del catálogo igual a la ficha de segmentos",
            (en_tarifa == ficha["codigos_A013"]).all()
            and (nuevos == ficha["codigos_nuevos_A013"]).all(),
            f"{en_tarifa.sum()} códigos, {nuevos.sum()} nuevos",
        )
    )
    return pd.DataFrame(filas)


def balance_stock(datos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Calcula el residuo del balance de stock por segmento y mes.

    residuo = S_t - (S_{t-1} + wholesale_t - matriculaciones_t), en coches. Las
    matriculaciones incluyen automatriculaciones: es el balance de los datos
    originales, no el de la demanda.
    """
    ventas_mes = (
        datos["ventas"]
        .groupby(["segmento", "t"], as_index=False)[["unidades", "u_automatriculacion"]]
        .sum()
    )
    balance = (
        datos["stock"][["segmento", "t", "periodo", "stock_total", "wholesale"]]
        .merge(ventas_mes, on=["segmento", "t"])
        .sort_values(["segmento", "t"])
    )
    balance["stock_anterior"] = balance.groupby("segmento")["stock_total"].shift()
    esperado = balance["stock_anterior"] + balance["wholesale"]
    balance["residuo"] = balance["stock_total"] - (esperado - balance["unidades"])
    balance["residuo_sin_automatriculacion"] = balance["stock_total"] - (
        esperado - (balance["unidades"] - balance["u_automatriculacion"])
    )
    return balance.reset_index(drop=True)


def serie_mensual_segmento(datos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Prepara una fila por segmento y mes con ventas, demanda, mercado y stock.

    `demanda_observada` son las matriculaciones menos las automatriculaciones. Es una
    cota inferior de la demanda en los meses con señal de falta de stock y está
    inflada en los meses con compras adelantadas: esos meses se marcan, no se
    corrigen. Las columnas de stock están vacías antes de A009.
    """
    ventas = datos["ventas"]
    claves = ["segmento", "t", "periodo", "anio", "mes", "fecha"]
    serie = ventas.groupby(claves, as_index=False).agg(
        matriculaciones=("unidades", "sum"),
        automatriculaciones=("u_automatriculacion", "sum"),
        ventas_especiales=("u_venta_especial", "sum"),
        renovacion_gama=("renovacion_gama", "max"),
    )
    serie["demanda_observada"] = serie["matriculaciones"] - serie["automatriculaciones"]

    mercado = (
        datos["mercado"]
        .groupby(["segmento", "t"], as_index=False)["unidades"]
        .sum()
        .rename(columns={"unidades": "mercado"})
    )
    serie = serie.merge(mercado, on=["segmento", "t"], how="left")
    serie["cuota"] = serie["matriculaciones"] / serie["mercado"]

    stock = datos["stock"][
        ["segmento", "t", "stock_total", "s_91_180", "s_mas_180", "s_sin_cliente",
         "wholesale"]
    ]
    serie = serie.merge(stock, on=["segmento", "t"], how="left")
    serie["stock_mas_90"] = serie["s_91_180"] + serie["s_mas_180"]
    serie = serie.drop(columns=["s_91_180", "s_mas_180"])

    economia = datos["economia"][["t", *SUCESOS, "dias_laborables", "semana_santa"]]
    serie = serie.merge(economia, on="t", how="left")

    primera_venta = (
        serie[serie["matriculaciones"] > 0].groupby("segmento")["t"].min().rename("t0")
    )
    serie = serie.merge(primera_venta, on="segmento")
    serie["en_venta"] = (serie["t"] >= serie["t0"]).astype(int)
    serie = serie.drop(columns="t0")

    # Sin dato de stock (antes de A009) no se puede detectar la restricción.
    libre = serie["s_sin_cliente"] / serie["matriculaciones"].replace(0, np.nan)
    serie["senal_falta_stock"] = (
        (libre < UMBRAL_STOCK_LIBRE).astype("Int64").where(serie["stock_total"].notna())
    )

    serie["segmento"] = pd.Categorical(serie["segmento"], SEGMENTOS, ordered=True)
    return serie.sort_values(["segmento", "t"]).reset_index(drop=True)


def exceso_adelanto(
    serie: pd.DataFrame,
    anio: str = "A012",
    meses_evento: tuple[int, ...] = (11, 12),
    meses_base: tuple[int, ...] = tuple(range(1, 11)),
    referencias: tuple[str, ...] = ("A009", "A010"),
    excluir: tuple[str, ...] = ("CSUV",),
    columna: str = "demanda_observada",
) -> pd.DataFrame:
    """Estima el exceso de demanda en los meses de compras adelantadas.

    Para cada año de referencia sin sucesos, el valor esperado de los meses del
    evento es el nivel de los meses base del año analizado multiplicado por la
    proporción evento/base de la referencia. El rango entre referencias mide la
    incertidumbre del método. Se agregan los segmentos con historia comparable.
    """
    datos = serie[~serie["segmento"].isin(excluir)]
    mensual = datos.groupby(["anio", "mes"])[columna].sum().unstack("mes")
    observado = mensual.loc[anio, list(meses_evento)].sum()
    base = mensual.loc[anio, list(meses_base)].sum()
    filas = []
    for referencia in referencias:
        proporcion = (
            mensual.loc[referencia, list(meses_evento)].sum()
            / mensual.loc[referencia, list(meses_base)].sum()
        )
        esperado = base * proporcion
        filas.append(
            {
                "referencia": referencia,
                "proporcion_evento_base": proporcion,
                "observado": observado,
                "esperado": esperado,
                "exceso": observado - esperado,
            }
        )
    return pd.DataFrame(filas)

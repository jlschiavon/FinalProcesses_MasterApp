from datetime import datetime
import pandas as pd

def asignar_turno(ts):
    h = ts.hour + ts.minute / 60
    if 7 <= h < 15:
        return "1st Shift"
    elif 15 <= h < 22.5:
        return "2nd Shift"
    else:
        return "3rd Shift"

import pandas as pd

def generar_union_final(df_alds=None, df_mes=None, df_oee=None):
    # Lista para acumular los DataFrames válidos
    dataframes = []

    if df_alds is not None and not df_alds.empty:
        dataframes.append(df_alds)

    if df_mes is not None and not df_mes.empty:
        dataframes.append(df_mes)

    if df_oee is not None and not df_oee.empty:
        dataframes.append(df_oee)

    if not dataframes:
        return pd.DataFrame(columns=["Shift", "Parte"])  # Devolver estructura vacía si no hay nada

    # Realizar un merge progresivo usando 'Shift' y 'Parte' como claves comunes
    df_result = dataframes[0]

    for df in dataframes[1:]:
        df_result = pd.merge(df_result, df, on=["Shift", "Parte"], how="outer")

    # Asegurar que las columnas claves existan aunque estén vacías
    df_result["Shift"] = df_result["Shift"].fillna("Sin turno").astype(str)
    df_result["Parte"] = df_result["Parte"].fillna("Sin parte").astype(str)

    # Rellenar valores faltantes
    df_result.fillna(0, inplace=True)

    return df_result


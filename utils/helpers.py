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

def generar_union_final(df_alds, df_mes, df_oee):
    tabla = pd.merge(df_mes, df_alds, on=["Shift", "Parte"], how="outer").fillna(0)
    tabla = pd.merge(tabla, df_oee, on=["Shift", "Parte"], how="left").fillna(0)

    tabla[["MES", "ALDS Serie", "ALDS Rework", "MES SCRAP", "OEE Serie", "OEE Rework", "OEE SCRAP"]] = tabla[
        ["MES", "ALDS Serie", "ALDS Rework", "MES SCRAP", "OEE Serie", "OEE Rework", "OEE SCRAP"]
    ].astype(int)

    tabla["Físico"] = ""

    return tabla[[
        "Shift", "Parte", "MES", "ALDS Serie", "ALDS Rework",
        "OEE Serie", "OEE Rework", "MES SCRAP", "Físico", "OEE SCRAP"
    ]]

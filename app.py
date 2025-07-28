import streamlit as st
from utils.load_clean_alds import cargar_alds
from utils.load_clean_mes import cargar_mes
from utils.load_clean_oee import cargar_oee
from utils.helpers import generar_union_final
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Master Daily Quantities Tracking CVT Final Processes", layout="wide")

st.title("📊 Master Daily Quantities Tracking - CVT Final Processes")
st.markdown("Sube los archivos diarios de ALDS, MES y OEE para obtener un resumen consolidado por parte y turno.")

alds_file = st.file_uploader("📄 Cargar archivo ALDS (.csv)", type=["csv"])
mes_file = st.file_uploader("📄 Cargar archivo MES (.xls, .xlsx)", type=["xls", "xlsx"])
oee_file = st.file_uploader("📄 Cargar archivo OEE (.csv)", type=["csv"])

if alds_file and mes_file and oee_file:
    df_alds = cargar_alds(alds_file)
    df_mes = cargar_mes(mes_file)
    df_oee = cargar_oee(oee_file)

    tabla_final = generar_union_final(df_alds, df_mes, df_oee)

    st.success("✅ Datos procesados correctamente")
    st.dataframe(tabla_final, use_container_width=True)

    output = BytesIO()
    tabla_final.to_excel(output, index=False, engine='openpyxl')
    st.download_button("📥 Descargar Excel", data=output.getvalue(), file_name="tabla_final_completa.xlsx")
else:
    st.warning("Por favor sube los tres archivos para continuar.")

"""
PARTE 2: Dashboard con Streamlit.
Ejecutar con:  streamlit run app.py
(antes hay que haber ejecutado scraper.py para generar pokemons.csv)
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tienda Pokémon", layout="wide")
st.title("🔴 Dashboard de la tienda Pokémon (ScrapeMe)")
st.write("Usa los filtros de la izquierda para explorar los datos extraídos con BeautifulSoup.")


# 1. CARGAR LOS DATOS (cache para no leer el CSV en cada interacción)
@st.cache_data
def cargar_datos():
    df = pd.read_csv("pokemons.csv")
    df["categorias"] = df["categorias"].fillna("")  # si no tiene categoría, texto vacío
    return df


df = cargar_datos()

# Un Pokémon puede tener varias categorías ("Pokemon, Seed").
# Creamos una fila por cada categoría para poder contar y agrupar por tipo.
df_tipos = df.assign(tipo=df["categorias"].str.split(", ")).explode("tipo")
lista_tipos = sorted(df_tipos["tipo"].dropna().unique())

# 2. FILTROS (barra lateral)
st.sidebar.header("Filtros")

# Búsqueda por nombre
busqueda = st.sidebar.text_input("Buscar por nombre")

# Filtro por tipo/categoría (si no se elige ninguno, se muestran todos)
tipos_elegidos = st.sidebar.multiselect("Tipo / categoría", lista_tipos)

# Filtro por rango de precio
precio_min = float(int(df["precio"].min()))       # redondeamos hacia abajo
precio_max = float(int(df["precio"].max()) + 1)   # redondeamos hacia arriba
rango_precio = st.sidebar.slider("Rango de precio (£)", precio_min, precio_max, (precio_min, precio_max))

# Filtro de disponibilidad
solo_stock = st.sidebar.checkbox("Solo Pokémon con stock")

# Aplicamos los filtros uno a uno sobre una copia del DataFrame
df_filtrado = df.copy()

if busqueda:
    df_filtrado = df_filtrado[df_filtrado["nombre"].str.contains(busqueda, case=False, regex=False)]

if tipos_elegidos:
    # "A|B" en str.contains significa "contiene A o B"
    df_filtrado = df_filtrado[df_filtrado["categorias"].str.contains("|".join(tipos_elegidos))]

df_filtrado = df_filtrado[
    (df_filtrado["precio"] >= rango_precio[0]) & (df_filtrado["precio"] <= rango_precio[1])
]

if solo_stock:
    df_filtrado = df_filtrado[df_filtrado["stock"] > 0]

# Si los filtros no dejan ningún Pokémon, avisamos y paramos
if df_filtrado.empty:
    st.warning("No hay Pokémon con esos filtros. Prueba a cambiarlos.")
    st.stop()

# 3. MÉTRICAS Y TABLA
col1, col2, col3 = st.columns(3)
col1.metric("Pokémon encontrados", len(df_filtrado))
col2.metric("Precio medio (£)", round(df_filtrado["precio"].mean(), 2))
col3.metric("Peso medio (kg)", round(df_filtrado["peso_kg"].mean(), 2))

st.subheader("Tabla de resultados")
st.dataframe(df_filtrado[["nombre", "categorias", "precio", "stock", "peso_kg"]])

# 4. GRÁFICOS
st.subheader("Gráficos")
graf1, graf2 = st.columns(2)

with graf1:
    st.write("**Los 10 Pokémon más caros (£)**")
    st.bar_chart(df_filtrado.nlargest(10, "precio").set_index("nombre")["precio"])

with graf2:
    st.write("**Precio medio (£) por tipo (top 10)**")
    df_filtrado_tipos = df_filtrado.assign(tipo=df_filtrado["categorias"].str.split(", ")).explode("tipo")
    precio_por_tipo = df_filtrado_tipos.groupby("tipo")["precio"].mean().sort_values(ascending=False).head(10)
    st.bar_chart(precio_por_tipo)

st.write("**Relación entre peso (kg) y precio (£)**")
st.scatter_chart(df_filtrado, x="peso_kg", y="precio")

# 5. ANÁLISIS CRÍTICO: ¿influye el peso en el precio?
st.subheader("¿Influye el peso del Pokémon en su precio?")
correlacion = df_filtrado["peso_kg"].corr(df_filtrado["precio"])

if pd.isna(correlacion):
    st.info("No hay datos suficientes para calcular la correlación.")
else:
    st.write(f"Correlación entre peso y precio: **{correlacion:.2f}**")
    if abs(correlacion) < 0.2:
        st.write("Es prácticamente cero: el peso de un Pokémon no tiene relación clara con su precio.")
    elif correlacion > 0:
        st.write("Es positiva: los Pokémon más pesados tienden a ser más caros.")
    else:
        st.write("Es negativa: los Pokémon más pesados tienden a ser más baratos.")

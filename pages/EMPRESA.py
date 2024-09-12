# IMPORTANDO AS BIBLIOTECAS E LIBRARIES
import pandas as pd
import folium
import streamlit as st
import streamlit_folium
from PIL import Image
import nbformat

# IMPORTANDO LIBRARIES
import plotly.io as pio
from streamlit_folium import folium_static
import plotly.graph_objects as go
import plotly.express as px
from haversine import haversine

# FUNÇÕES
def clean_code(df1):

    """ESTA FUNÇÃO SERVE PARA LIMPAR O DATAFRAME
        Tipos de limpeza:
        1. Remoção valores NaN
        2. Conversão tipo de coluna
        3. Remoção de espaços vazios em texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna tempo Time_taken(min)

        Imput: Dataframe
        Output: Dataframe
    """    
    # # LIMPEZA E TRATAMENTO DOS DADOS #

    # 1. Removendo valores 'NaN '

    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # Conferencia de valores vazios ou NaN
    # colunas_com_nan = df1.columns[df1.isin(['NaN ']).any()]
    # print(colunas_com_nan)

    # 2. Convertendo tipos de dados

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # Checando se as conversões foram realizadas
    # df1.dtypes.reset_index()

    # 3. Removendo os espaços dentro de strings/texto/object

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()

    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()

    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()

    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()

    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 4. Limpando coluna time_taken

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(
        lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

#-------------------------------- Inicio da estrutura logica do código ------------------------------------------------------------------------------------------#

# CARREGANDO BANCO DE DADOS
df = pd.read_csv('Dataset/train.csv')

# EXECUTANDO LIMPEZA DO BANCO DE DADOS
df1 = clean_code(df)

# ==============================
# Barra lateral
# ==============================
st.set_page_config(page_title='VISÃO CLIENTE', page_icon='😋', layout='wide', initial_sidebar_state='auto', menu_items=None)

st.header('Marketplace - Visão Cliente')

image = Image.open('cury_logo.jpg')

st.sidebar.image(image, width=270)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### Fastest Delivery in town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('### Selecione uma data limite')

from datetime import datetime 

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium','High', 'Jam'],
    default=['Low', 'Medium','High', 'Jam']
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Thulle Lima')

# Filtro data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro transito
linhas_selecionadas = df1['Road_traffic_density'] .isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# ==============================
# Layout no Streamlit
# ==============================

tab1, tab2, tab3 = st.tabs(['Visão gerencial','Visão tática', 'Visão geográfica'])

with tab1:
    with st.container():
        cols = ['ID', 'Order_Date']

        df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
        fig=px.bar(df_aux, x='Order_Date', y='ID', title='Número de pedidos por dia')
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)    
        with col1:
            st.header('Traffic order share')
            df_aux = df1.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
            df_aux['entregas_perc']=df_aux['ID']/df_aux['ID'].sum()
            fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
            st.plotly_chart(fig,use_container_width=True)
        
        with col2:
            st.header('Traffic order city')
            st.markdown('# Coluna 2')
            df_aux = df1.loc[:,['ID', 'City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('# Country maps')
    df_aux = df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude', 'Delivery_location_longitude' ]].groupby(['City','Road_traffic_density']).median().reset_index()
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info[['City','Road_traffic_density']]).add_to(map)
    folium_static(map, width=1024, height=600) 

with tab2:
    with st.container():
        st.markdown('# Order by week')
        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
        df_aux = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
        fig = px.line(df_aux, x='week_of_year', y='ID')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('# Order by year')
        df_aux01 = df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux02 = df1.loc[:,['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
        df_aux = pd.merge(df_aux01, df_aux02, how='inner',on='week_of_year')
        df_aux['order_by_delivery'] = df_aux['ID']/df_aux['Delivery_person_ID']

        fig = px.line(df_aux, x='week_of_year', y='order_by_delivery')
        st.plotly_chart(fig, use_container_width=True)

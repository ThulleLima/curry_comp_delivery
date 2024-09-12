# IMPORTANDO AS BIBLIOTECAS E LIBRARIES
import pandas as pd
import numpy as np
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

#-------------------------------- Inicio da estrutura logica do código --------------------------------------------------------------------------------------------#

# CARREGANDO BANCO DE DADOS
df = pd.read_csv('Dataset\\train.csv')

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

tab1, = st.tabs(['Visão entregadores'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #st.subheader('Maior de idade')
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)

        with col2:
            #st.subheader('Menor de idade')
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)

        with col3:
            #st.subheader('Melhor condição de veiculo')
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)

        with col4:
            #st.subheader('Pior condição de veiculo')
            pior_condicao = df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)

    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')

        col1,col2 = st.columns(2)
        with col1:
            st.markdown ('##### Avaliação médias por entregador')
            aval_md_ent = (df1.loc[:,['Delivery_person_Ratings', 'Delivery_person_ID']]
                          .groupby('Delivery_person_ID')
                          .mean()
                          .reset_index())
            st.dataframe(aval_md_ent)

        with col2:
            st.markdown ('##### Avaliação média por transito')
            aval_md_trs = (df1.loc[:,['Delivery_person_Ratings', 'Road_traffic_density']]
                              .groupby('Road_traffic_density')
                              .agg({'Delivery_person_Ratings':['mean','std']}))
            aval_md_trs.columns = ['delivery_mean', 'delivery_std']
            aval_md_trs = aval_md_trs.reset_index()
            st.dataframe(aval_md_trs)

            st.markdown ('##### Avaliação média por clima')
            aval_md_clm = (df1.loc[:,['Delivery_person_Ratings', 'Weatherconditions']]
                              .groupby('Weatherconditions')
                              .agg({'Delivery_person_Ratings':['mean','std']}))
            aval_md_clm.columns = ['delivery_mean', 'delivery_std']
            aval_md_clm = aval_md_clm.reset_index()
            st.dataframe(aval_md_clm)

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Top entregadores mais rápidos')
            df2 = (df1.loc[:,['Delivery_person_ID','City', 'Time_taken(min)']]
                      .groupby(['City','Delivery_person_ID'])
                      .mean()
                      .sort_values(['City','Time_taken(min)'], ascending=True)
                      .reset_index())
            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

            df3 = pd.concat([df_aux01,df_aux02,df_aux03]).reset_index(drop=True)
            st.dataframe(df3)

        with col2:
            st.subheader('Top entregadores mais lentos')
            df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                      .groupby(['City', 'Delivery_person_ID'])
                      .mean()
                      .sort_values(['City', 'Time_taken(min)'], ascending=False).reset_index())

            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux01 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux01 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
            
            df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
            st.dataframe(df3)
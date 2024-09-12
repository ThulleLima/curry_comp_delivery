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
tab1, = st.tabs(['Visão gerencial'])

with tab1:

    with st.container():
        st.title('Overall metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            ID_unico = len(df1.loc[:,'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', ID_unico)

        with col2:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude','Restaurant_latitude', 'Restaurant_longitude']
            df1['distance'] = df1.loc[:,cols].apply( lambda x:
                                        haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                  (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            avg_distance = np.round(df1['distance'].mean(),2)
            col2.metric('A distancia media das entregas', avg_distance)                             

        with col3:
            df_aux = (df1.loc[:,['Time_taken(min)', 'Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)':['mean','std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'],2)
            col3.metric('Tempo médio de entrega c/ festival', df_aux)

        with col4:
            df_aux = (df1.loc[:,['Time_taken(min)', 'Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)':['mean','std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'],2)
            col4.metric('Desvio padrão de entrega c/ festival', df_aux)

        with col5:
            df_aux = (df1.loc[:,['Time_taken(min)', 'Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)':['mean','std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'],2)
            col5.metric('Tempo médio de entrega s/ festival', df_aux)

        with col6:
            df_aux = (df1.loc[:,['Time_taken(min)', 'Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)':['mean','std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'std_time'],2)
            col6.metric('Desvio padrão de entrega s/ festival', df_aux)

    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)

        with col1:
            st.title('Tempo médio de entregas por cidade')
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df1['distance'] = df1.loc[:, cols].apply(lambda x:
                                            haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                      (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)
            avg_distance = df1.loc[:,['City', 'distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0.01,0.01,0.01])])
            st.plotly_chart(fig)

        with col2:
            st.title('Tempo médio de entregas por cidade')
            df_aux = (df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                         .groupby(['City', 'Type_of_order'])
                         .agg({'Time_taken(min)':['mean','std']}))
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)

    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do tempo')

        col1, col2 = st.columns(2)
        with col1:
            df_aux = df1.loc[:, ['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']} )
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = go.Figure()
            fig.add_trace( go.Bar(name='Control', x=df_aux['City'] ,y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)

        with col2:
            df_aux = (df1.loc[:,['City', 'Time_taken(min)', 'Road_traffic_density']]
                         .groupby(['City','Road_traffic_density'])
                         .agg({'Time_taken(min)':['mean', 'std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
            color='std_time', color_continuous_scale='RdBu',
            color_continuous_midpoint=np.average(df_aux['std_time']))
            
            st.plotly_chart(fig)

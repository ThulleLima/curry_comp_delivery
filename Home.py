import streamlit as st
from PIL import Image

st.set_page_config(    
    page_title= 'Home',
    page_icon='🏠'
)

image = Image.open('cury_logo.jpg')

st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### Fastest Delivery in town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')

st.markdown (
    """ Growth Dashboard foi construido para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar este Growth Dashboard?

    - Visão Empresa: 
      - Visão Gerencial: Métricas gerais de comportamento.
      - Visão Tática: Indicadores semanais de crescimento.
      - Visão geografica: Insights de geolocalização
    - Visão entregador:
      - Acompanhamento dos indicadores semanais de crescimento 
    - Visão Restaurante:
      - Indicadores semanais de crescimento dos restaurantes

    ### Ask for Help
    - Time de Data Science no Discord
       - @Thullelima
""")
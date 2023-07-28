import streamlit as st
import pandas as pd
from datetime import datetime, timedelta,  date
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import altair as alt


st.title("Detecção de Discurso de Ódio e Preconceito nas Redes")
st.sidebar.image('tera.png')

data = pd.read_csv(r"C:\Users\daniela.nomura_ifood\projeto_tera-env\group_info_df.csv") #path folder of the data file

# Crie um espaço reservado para o slider de datas
slider_placeholder = st.empty()
 
# Atualize o slider de datas com base no intervalo de tempo selecionado
data_inicial = date(2022, 9, 1)
data_final = date(2022, 11, 1)
 

data_selecionada = st.sidebar.slider(
    "Selecione um intervalo de datas para a análise",
    min_value=data_inicial,
    max_value=data_final,
    value=(data_inicial, data_final),
    step=timedelta(days=1),
    format="YYYY-MM-DD"
)

data['day2'] = pd.to_datetime(data['day']).dt.date
range_data = ((data['day2'] >= data_selecionada[0]) & (data['day2'] <= data_selecionada[1]))
df = data.loc[range_data]

options = df['DS_GENERO'].unique().tolist()
selected_gen = st.sidebar.multiselect('Selecione o Genero dos(as) Candidatos(as)',options)

options_raca = df['DS_COR_RACA'].unique().tolist()
selected_raca = st.sidebar.multiselect('Selecione a Cor/Raça dos(as) Candidatos(as)',options_raca)

options_esc = df['DS_GRAU_INSTRUCAO'].unique().tolist()
selected_esc = st.sidebar.multiselect('Selecione o Grau de Escolaridade dos(as) Candidatos(as)',options_esc)


filtered_df = df[((df["DS_GENERO"].isin(selected_gen)) 
                  & (df["DS_COR_RACA"].isin(selected_raca))
                  & (df["DS_GRAU_INSTRUCAO"].isin(selected_esc)))]

filtered_df['is_offensive'] = filtered_df['class_label'].astype(int)  

ofensivo = sum(1 for item in filtered_df['class_label'] if item==True)
candidatos = sum(1 for item in filtered_df['user_is_candidate'] if item==True)

# create two columns
kpi1,kpi2, kpi3 = st.columns(3)

kpi1.metric(
    label="Total de Mensagens",
    value=filtered_df['id'].sum()
)

kpi2.metric(
    label="Mensagens de Candidatos",
    value=candidatos
)

kpi3.metric(
    label="% de Mensagens ofensivas",
    value=round(100*((ofensivo)/(filtered_df['id'].sum())),2),
)

graf = (filtered_df.groupby('day',as_index=False).agg({'id':sum,'is_offensive':sum})        )
graf['perc_of']=round(100*(graf['is_offensive']/graf['id']),2)

graf_layer=(
   alt.Chart(graf).mark_bar().encode(
   x='day',
   y=alt.Y('id', title='# Mensagens')   
   )
   .interactive()
    )
    
st.altair_chart((graf_layer).interactive(), use_container_width=True)


graf_layer2=(
   alt.Chart(graf).mark_line(point=True,color="#ed3b09").encode(
   x='day',
   y=alt.Y(('perc_of'), title='% discurso de odio')  
   )
   .configure_mark(
    opacity=0.2,
    color='#ed3b09'
   )
   .interactive()
    )
    
st.altair_chart((graf_layer2).interactive(), use_container_width=True)
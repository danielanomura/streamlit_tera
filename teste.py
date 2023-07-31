import streamlit as st
import pandas as pd
from datetime import datetime, timedelta,  date
import matplotlib.pyplot as plt
import altair as alt


st.title("Detecção de Discurso de Ódio e Viéses nas Redes")
st.sidebar.image('tera.png')

data = pd.read_csv(r"group_info_df_v2.csv") #path folder of the data file

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

if not selected_gen:
    selected_gen = ['FEMININO', 'MASCULINO']

if not selected_raca:
    selected_raca = ['PARDA', 'INDÍGENA', 'PRETA', 'BRANCA']

if not selected_esc:
    selected_esc = ['ENSINO FUNDAMENTAL INCOMPLETO', 'SUPERIOR INCOMPLETO', 'SUPERIOR COMPLETO']
 
filtered_df = df[((df["DS_GENERO"].isin(selected_gen)) 
                  & (df["DS_COR_RACA"].isin(selected_raca))
                  & (df["DS_GRAU_INSTRUCAO"].isin(selected_esc)))]

filtered_df['is_offensive'] = filtered_df['class_label'].astype(int)  
filtered_df['qtt_offensive'] = (filtered_df['is_offensive'])*(filtered_df['id'])


ofensivo = filtered_df[filtered_df['is_offensive']==1]['id'].sum()
posts = filtered_df[filtered_df['is_reply']==0]['id'].sum()
post_ofensivo = filtered_df.loc[(filtered_df['is_reply']==0) & (filtered_df['is_offensive']==1), 'id'].sum()

respostas = filtered_df[filtered_df['is_reply']==1]['id'].sum()
respostas_ofensivo = filtered_df.loc[(filtered_df['is_reply']==1) & (filtered_df['is_offensive']==1), 'id'].sum()
#filtered_df[filtered_df['is_reply']==0 & filtered_df['is_offensive']==1]['id'].sum()
#ofensivo = sum(df.get(filtered_df['id']) for item in filtered_df['class_label'] if item==True)

candidatos = filtered_df[filtered_df['user_is_candidate']==1]['id'].sum()

# create two columns
kpi1,kpi2, kpi3 = st.columns(3)

kpi1.metric(
    label="Total de Mensagens",
    value=filtered_df['id'].sum()
)

kpi2.metric(
    label="Mensagens de candidatos",
    value=candidatos
    
)

kpi3.metric(
    label="Mensagens de ódio",
    value=ofensivo
)

kpi4,kpi5, kpi6 = st.columns(3)

kpi4.metric(
    label="% de Mensagens de ódio",
    value=round(100*((ofensivo)/(filtered_df['id'].sum())),2)
    
)

kpi5.metric(
    label="% Mensagens de ódio postadas",
    value= round(100*((post_ofensivo)/(posts)),2)
)

kpi6.metric(
    label="% Mensagens de ódio nas respostas",
    value=round(100*((respostas_ofensivo)/(respostas)),2)
)

graf = (filtered_df.groupby('day',as_index=False).agg({'id':sum,'qtt_offensive':sum}) 
       )

graf['perc_of']=round(100*(graf['qtt_offensive']/graf['id']),2)

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

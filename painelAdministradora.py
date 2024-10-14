import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import getAdministradora, getSegmento, getBaseConsolidadaSegmentoMensal, formataData, formataNumero, getBaseSegmentoMensal, getBaseContabil
from streamlit_extras.metric_cards import style_metric_cards


def show():

    st.title('Panorama Administradoras')
    st.text('Selecione uma administradora para iniciar')
    st.text('')
    
    
    with st.spinner('Aguarde carregando dados...'):
        
        st.sidebar.text(' ')
        st.sidebar.text('Filtros')
        
        
        administradoras = getAdministradora()
        administradorasDict = dict(zip(administradoras['strNomeAdministradora'], administradoras['idAdministradora']))
        administradorasDict = {'Selecione': 0, **administradorasDict}
        administradoraSelecionada = st.sidebar.selectbox("Selecione uma Administradora", list(administradorasDict.keys()))
        
        segmentos = getSegmento()
        segmentosDict = dict(zip(segmentos['strNomeSegmento'], segmentos['idSegmento']))
        segmentosDict = {'Selecione': 0, **segmentosDict}
        segmentoSelecionado = 'Selecione'#st.sidebar.selectbox("Selecione um Segmento", list(segmentosDict.keys()))
        
        
        
        if administradorasDict[administradoraSelecionada] > 0:
            
            st.divider()
            st.text(f'Administradora: {administradoraSelecionada}')
            st.caption(f'Segmento: Todos')
            
            
            df = getBaseConsolidadaSegmentoMensal(administradorasDict[administradoraSelecionada],segmentosDict[segmentoSelecionado],0)
            
            
            #criando novas colunas
            df['intQuantidadeTotalCotasInadimplentesAtivas'] = df['intQuantidadeCotasAtivasContempladasInadimplente'] + df['intQuantidadeCotasAtivasNaoContempladasInadimplentes']
            df['intQuantidadeTotalCotasAtivas'] = df['intQuantidadeTotalCotasInadimplentesAtivas'] + df['intQuantidadeCotasAtivasAdimplentes']
            
            
            df['fltIndiceCotasCanceladas']= (df['intQuantidadeCotasExcluidas'] /(df['intQuantidadeTotalCotasAtivas'] + df['intQuantidadeCotasExcluidas'])) * 100.00
            df['fltIndiceCotasCanceladas'] = df['fltIndiceCotasCanceladas'].fillna(0)
            
            
            df['dtBase'] = df['dtBase'].apply(pd.to_datetime)
            df = df.sort_values(by='dtBase')
            
            dataMaxima = df['dtBase'].max()
            
            #anoAnterior = dataMaxima - pd.DateOffset(years=1)
            #semestreAnterior = dataMaxima - pd.DateOffset(months=6)

            st.caption(f'Data base: {formataData(dataMaxima)}')
            #st.caption(f'Semestre Anterior: {formataData(semestreAnterior)}')
            #st.caption(f'Ano Anterior: {formataData(anoAnterior)}')
            st.divider()

            
            dfDataMaxima = df[df['dtBase'] == dataMaxima]
            #dfSemestreAnterior = df[df['dtBase'] == semestreAnterior]
            #dfAnoAnterior = df[df['dtBase'] == anoAnterior]            
            #st.dataframe(df)
            
            totais = dfDataMaxima[['intQuantidadeTotalCotasAtivas',
                                   'intQuantidadeCotasAtivasContempladasMes',
                                   'intQuantidadeCotasComercializadasMes', 
                                   'intQuantidadeTotalCotasInadimplentesAtivas', 
                                   'intQuantidadeGruposAtivos', 
                                   'intQuantidadeGruposConstituidosMes', 
                                   'intQuantidadeGruposEncerradosMes',
                                   'intQuantidadeCotasExcluidas']].sum()
            
            
            mediasSM = (totais[0]/(totais[0] + totais[7])) * 100
            
            st.subheader('1 - Valores base consolidada por segmento')
            st.text('')

            st.text('1.1 - Grupos')
            st.text('')

            
            #--------------------------------CARDS GRUPOS ------------------------------------
            col1, col2, col3 = st.columns(3)

            col1.metric(label="Grupos Ativos", value=formataNumero(totais[4],1))
            col2.metric(label="Grupos Constituídos no Mês", value=formataNumero(totais[5],1))
            col3.metric(label="Grupos Encerrados no Mês", value=formataNumero(totais[6],1))
            #--------------------------------------------------------------------------------------------            
            

            st.text('1.1.1 - Grupos Ativos por Segmento')
            st.text('')
            
            
            #--------------------------------GRÁFICO SEGMENTOS POR GRUPO ATIVO------------------------------------
            fig = go.Figure(data=[go.Pie(labels=dfDataMaxima['strNomeSegmento'].tolist(), values=dfDataMaxima['intQuantidadeGruposAtivos'].tolist(), hole=0.5)])     
            fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=15)     

            st.plotly_chart(fig)
            #--------------------------------------------------------------------------------------------
            
            
            #--------------------------------DF SEGMENTOS POR GRUPO ATIVOS------------------------------------
            df_segmentos = dfDataMaxima.groupby('strNomeSegmento')['intQuantidadeGruposAtivos'].sum().reset_index()

            total_grupos_ativos = df_segmentos['intQuantidadeGruposAtivos'].sum()

            df_segmentos['% do Total'] = (df_segmentos['intQuantidadeGruposAtivos'] / total_grupos_ativos) * 100

            df_segmentos = df_segmentos.sort_values(by='intQuantidadeGruposAtivos', ascending=False)

            linha_total = pd.DataFrame({
                'strNomeSegmento': ['Total'], 
                'intQuantidadeGruposAtivos': [total_grupos_ativos], 
                '% do Total': [100.0]
            })

            df_com_total = pd.concat([df_segmentos, linha_total], ignore_index=True)

            st.dataframe(df_com_total, use_container_width=True)
            #-------------------------------------------------------------------------------------------
            
            st.text('1.1.2 - Gráficos Evolução Grupos')
            st.text('')
            

            #-------------------------------GRÁFICO GRUPOS ENCERRADOS E CONSTITUÍDOS ---------------------------------------
            df_filtered = df.dropna(subset=['intQuantidadeGruposConstituidosMes', 'intQuantidadeGruposEncerradosMes', 'dtBase'])

            # Realizar soma cumulativa (acumular valores ao longo do tempo)
            df_filtered['intQuantidadeGruposConstituidosMes'] = df_filtered['intQuantidadeGruposConstituidosMes'].cumsum()
            df_filtered['intQuantidadeGruposEncerradosMes'] = df_filtered['intQuantidadeGruposEncerradosMes'].cumsum()

            # Reorganizar os dados para o formato long
            df_melted = df_filtered.melt(id_vars='dtBase', 
                                        value_vars=['intQuantidadeGruposConstituidosMes', 'intQuantidadeGruposEncerradosMes'],
                                        var_name='Tipo de Grupo', 
                                        value_name='Quantidade Acumulada')
            
            fig = px.line(df_melted, 
                        x='dtBase', 
                        y='Quantidade Acumulada', 
                        color='Tipo de Grupo',  
                        markers=True,
                        labels={'Quantidade Acumulada': 'Quantidade Acumulada de Grupos', 'dtBase': 'Período'},
                        )

            st.text('1.1.1 - Variação Acumulada da Quantidade de Grupos ao Longo do Tempo')
            
            st.plotly_chart(fig)
            #-------------------------------------------------------------------------------------------            

            
            
            #-------------------------------GRÁFICO GRUPOS ENCERRADOS E CONSTITUÍDOS ---------------------------------------
            # Filtrar os dados
            df_filtered = df.dropna(subset=['intQuantidadeGruposEncerradosMes', 'strNomeSegmento', 'dtBase'])

            # Calcular a soma cumulativa por segmento
            df_filtered['intQuantidadeGruposEncerradosAcumulada'] = df_filtered.groupby('strNomeSegmento')['intQuantidadeGruposEncerradosMes'].cumsum()

            # Criar o gráfico com a quantidade acumulada
            fig = px.line(df_filtered, 
                        x='dtBase', 
                        y='intQuantidadeGruposEncerradosAcumulada', 
                        color='strNomeSegmento', 
                        markers=True,
                        labels={'intQuantidadeGruposEncerradosAcumulada': 'Quantidade Acumulada de Grupos Encerrados', 
                                'dtBase': 'Período'}
                        )

            
            st.text('1.1.3 - Variação Acumulada da Quantidade de Grupos Encerrados ao Longo do Tempo por Segmento')
            st.plotly_chart(fig)
            #-------------------------------------------------------------------------------------------            
            
            #-------------------------------GRÁFICO GRUPOS ATIVOS ---------------------------------------
            df_filtered = df.dropna(subset=['intQuantidadeGruposAtivos', 'strNomeSegmento', 'dtBase'])
            fig = px.line(df_filtered, 
                    x='dtBase', 
                    y='intQuantidadeGruposAtivos', 
                    color='strNomeSegmento',
                    markers=True,
                    labels={'intQuantidadeGruposAtivos': 'Quantidade Grupos Ativos', 'dtBase': 'Período'},
                )
            st.text('1.1.4 - Variação da Quantidade de Grupos Ativos ao Longo do Tempo por Segmento')
            st.plotly_chart(fig)            
            #-------------------------------------------------------------------------------------------            

            
            st.text('1.2 - Cotas')
            st.text('')
            
            #---------------------------- CARDS COTAS -------------------------------------------------            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(label="Cotas Ativas", value=formataNumero(totais[0],1))
            col2.metric(label="Cotas Contempladas", value=formataNumero(totais[1],1))
            col3.metric(label="Cotas Comercializadas no Mês", value=formataNumero(totais[2],1))
            col4.metric(label="Cotas Inadimplentes", value=formataNumero(totais[3],1))
            
            style_metric_cards(background_color='#0E1117', border_color= '#2B2E33', border_left_color= '#29B09D')
            
            #-------------------------------------------------------------------------------------------            

            st.text('1.2.1 - Cotas Ativas ')
            st.text('')

            
            st.text('1.2.1.1 - Cotas Ativas por Segmento')
            st.text('')

            #--------------------------------GRÁFICO SEGMENTOS POR GRUPO ATIVO------------------------------------
            fig = go.Figure(data=[go.Pie(labels=dfDataMaxima['strNomeSegmento'].tolist(), values=dfDataMaxima['intQuantidadeTotalCotasAtivas'].tolist(), hole=0.5)])     
            fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=15)     

            st.plotly_chart(fig)
            #--------------------------------------------------------------------------------------------
            
            
            #--------------------------------DF SEGMENTOS POR GRUPO ATIVOS------------------------------------
            df_segmentos = dfDataMaxima.groupby('strNomeSegmento')['intQuantidadeTotalCotasAtivas'].sum().reset_index()

            total_grupos_ativos = df_segmentos['intQuantidadeTotalCotasAtivas'].sum()

            df_segmentos['% do Total'] = (df_segmentos['intQuantidadeTotalCotasAtivas'] / total_grupos_ativos) * 100

            df_segmentos = df_segmentos.sort_values(by='intQuantidadeTotalCotasAtivas', ascending=False)

            linha_total = pd.DataFrame({
                'strNomeSegmento': ['Total'], 
                'intQuantidadeTotalCotasAtivas': [total_grupos_ativos], 
                '% do Total': [100.0]
            })

            df_com_total = pd.concat([df_segmentos, linha_total], ignore_index=True)

            st.dataframe(df_com_total, use_container_width=True)
            #-------------------------------------------------------------------------------------------

            st.text('1.2.1.2 - Evolução das Cotas Ativas')
            st.text('')
            
            #-------------------------------------------------------------------------------------------
            df_totais_por_data = df.groupby('dtBase')['intQuantidadeTotalCotasAtivas'].sum().reset_index()

            
            df_totais_por_data = df_totais_por_data.sort_values(by='dtBase')

            
            fig = px.line(df_totais_por_data, 
                        x='dtBase', 
                        y='intQuantidadeTotalCotasAtivas', 
                        markers=True,
                        labels={'intQuantidadeTotalCotasAtivas': 'Quantidade Total de Cotas Ativas', 'dtBase': 'Data Base'},
                        )

            
            st.plotly_chart(fig)
            #-------------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------------
            st.text('1.2.1.2 - Crescimento Percentual e Quantidade de Cotas Ativas em Dezembro por Ano')
            st.text('')
            
            
            df['dtBase'] = pd.to_datetime(df['dtBase'], format='%Y-%m-%d')

            df_dezembro = df[df['dtBase'].dt.month == 12]

            df_dezembro['Ano'] = df_dezembro['dtBase'].dt.year

            df_totais_por_ano_dezembro = df_dezembro.groupby('Ano')['intQuantidadeTotalCotasAtivas'].sum().reset_index()

            df_totais_por_ano_dezembro = df_totais_por_ano_dezembro.sort_values(by='Ano')

            df_totais_por_ano_dezembro['Crescimento (%)'] = df_totais_por_ano_dezembro['intQuantidadeTotalCotasAtivas'].pct_change() * 100

            df_totais_por_ano_dezembro['Crescimento (%)'].fillna(0, inplace=True)

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=df_totais_por_ano_dezembro['Ano'], 
                y=df_totais_por_ano_dezembro['intQuantidadeTotalCotasAtivas'], 
                name='Quantidade de Cotas Ativas (Dezembro)',
                marker_color='rgba(0, 123, 255, 0.6)',
                text=df_totais_por_ano_dezembro['intQuantidadeTotalCotasAtivas'],  # Adicionar rótulo dos valores
                textposition='auto',
                yaxis='y1'
            ))

            fig.add_trace(go.Scatter(
                x=df_totais_por_ano_dezembro['Ano'], 
                y=df_totais_por_ano_dezembro['Crescimento (%)'], 
                name='Crescimento Percentual (%)',
                mode='lines+markers+text',  # Adiciona rótulos aos pontos da linha
                marker_color='rgba(255, 123, 0, 0.8)',
                text=df_totais_por_ano_dezembro['Crescimento (%)'].round(2).astype(str) + '%',  # Rótulo com percentual
                textposition='top center',
                yaxis='y2'
            ))

            fig.update_layout(
                xaxis_title='Ano',
                yaxis=dict(
                    title='Quantidade de Cotas Ativas',
                    titlefont=dict(color='rgba(0, 123, 255, 0.6)'),
                    tickfont=dict(color='rgba(0, 123, 255, 0.6)')
                ),
                yaxis2=dict(
                    title='Crescimento Percentual (%)',
                    titlefont=dict(color='rgba(255, 123, 0, 0.8)'),
                    tickfont=dict(color='rgba(255, 123, 0, 0.8)'),
                    overlaying='y',
                    side='right'
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                )
            )

            st.plotly_chart(fig)
            #-------------------------------------------------------------------------------------------
                       
            st.text('1.2.1.2 - Evoluçãos das Cotas Ativas por Segmento')
            st.text('')
            
            
            #-------------------------------------------------------------------------------------------

            df_totais_por_data = df.groupby(['dtBase', 'strNomeSegmento'])['intQuantidadeTotalCotasAtivas'].sum().reset_index()

            
            df_totais_por_data = df_totais_por_data.sort_values(by='dtBase')

            
            fig = px.line(df_totais_por_data, 
                        x='dtBase', 
                        y='intQuantidadeTotalCotasAtivas', 
                        color='strNomeSegmento',  # Segmentar por cor
                        markers=True,
                        labels={'intQuantidadeTotalCotasAtivas': 'Quantidade Total de Cotas Ativas', 'dtBase': 'Data Base'}
                        )

            
            st.plotly_chart(fig)
            #-------------------------------------------------------------------------------------------
            
            st.text('1.2.2 - Cotas Comercializadas no Mês')
            st.text('')

            
            st.text('1.2.2.1 - Cotas Comercializadas por Segmento')
            st.text('')

            #--------------------------------GRÁFICO SEGMENTOS POR GRUPO ATIVO------------------------------------
            fig = go.Figure(data=[go.Pie(labels=dfDataMaxima['strNomeSegmento'].tolist(), values=dfDataMaxima['intQuantidadeCotasComercializadasMes'].tolist(), hole=0.5)])     
            fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=15)     

            st.plotly_chart(fig)
            #--------------------------------------------------------------------------------------------
            
            
            #--------------------------------DF SEGMENTOS POR GRUPO ATIVOS------------------------------------
            df_segmentos = dfDataMaxima.groupby('strNomeSegmento')['intQuantidadeCotasComercializadasMes'].sum().reset_index()

            total_grupos_ativos = df_segmentos['intQuantidadeCotasComercializadasMes'].sum()

            df_segmentos['% do Total'] = (df_segmentos['intQuantidadeCotasComercializadasMes'] / total_grupos_ativos) * 100

            df_segmentos = df_segmentos.sort_values(by='intQuantidadeCotasComercializadasMes', ascending=False)

            linha_total = pd.DataFrame({
                'strNomeSegmento': ['Total'], 
                'intQuantidadeCotasComercializadasMes': [total_grupos_ativos], 
                '% do Total': [100.0]
            })

            df_com_total = pd.concat([df_segmentos, linha_total], ignore_index=True)

            st.dataframe(df_com_total, use_container_width=True)
            #-------------------------------------------------------------------------------------------

            st.text('1.2.2.2 - Evolução das Cotas Comecializadas por Mês')
            st.text('')
            
            #-------------------------------------------------------------------------------------------
            df_totais_por_data = df.groupby('dtBase')['intQuantidadeCotasComercializadasMes'].sum().reset_index()

            
            df_totais_por_data = df_totais_por_data.sort_values(by='dtBase')

            
            fig = px.line(df_totais_por_data, 
                        x='dtBase', 
                        y='intQuantidadeCotasComercializadasMes', 
                        markers=True,
                        labels={'intQuantidadeCotasComercializadasMes': 'Quantidade Total de Cotas Cormecializadas', 'dtBase': 'Data Base'},
                        )

            
            st.plotly_chart(fig)
            #-------------------------------------------------------------------------------------------
            
                       
            st.text('1.2.2.3 - Evoluçãos das Cotas Ativas por Segmento')
            st.text('')
            
            
            #-------------------------------------------------------------------------------------------

            df_totais_por_data = df.groupby(['dtBase', 'strNomeSegmento'])['intQuantidadeCotasComercializadasMes'].sum().reset_index()

            
            df_totais_por_data = df_totais_por_data.sort_values(by='dtBase')

            
            fig = px.line(df_totais_por_data, 
                        x='dtBase', 
                        y='intQuantidadeCotasComercializadasMes', 
                        color='strNomeSegmento',  # Segmentar por cor
                        markers=True,
                        labels={'intQuantidadeCotasComercializadasMes': 'Quantidade Total de Cotas Comercializadas', 'dtBase': 'Data Base'}
                        )

            
            st.plotly_chart(fig)
            #-------------------------------------------------------------------------------------------            
            
            
            
            st.text('1.2.3 - Cotas Inadimplentes ')
            st.text('')

            
            st.text('1.2.3.1 - Cotas Inadimplentes por Segmento')
            st.text('')

            #--------------------------------GRÁFICO SEGMENTOS POR GRUPO ATIVO------------------------------------
            fig = go.Figure(data=[go.Pie(labels=dfDataMaxima['strNomeSegmento'].tolist(), values=dfDataMaxima['intQuantidadeTotalCotasInadimplentesAtivas'].tolist(), hole=0.5)])     
            fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=15)     

            st.plotly_chart(fig)
            #--------------------------------------------------------------------------------------------
            
            
            #--------------------------------DF SEGMENTOS POR GRUPO ATIVOS------------------------------------
            df_segmentos = dfDataMaxima.groupby('strNomeSegmento')['intQuantidadeTotalCotasInadimplentesAtivas'].sum().reset_index()

            total_grupos_ativos = df_segmentos['intQuantidadeTotalCotasInadimplentesAtivas'].sum()

            df_segmentos['% do Total'] = (df_segmentos['intQuantidadeTotalCotasInadimplentesAtivas'] / total_grupos_ativos) * 100

            df_segmentos = df_segmentos.sort_values(by='intQuantidadeTotalCotasInadimplentesAtivas', ascending=False)

            linha_total = pd.DataFrame({
                'strNomeSegmento': ['Total'], 
                'intQuantidadeTotalCotasInadimplentesAtivas': [total_grupos_ativos], 
                '% do Total': [100.0]
            })

            df_com_total = pd.concat([df_segmentos, linha_total], ignore_index=True)

            st.dataframe(df_com_total, use_container_width=True)
            #-------------------------------------------------------------------------------------------

            st.text('1.2.3.2 - Evolução das Cotas Inadimplentes')
            st.text('')
            
            #-------------------------------------------------------------------------------------------
            df_totais_por_data = df.groupby('dtBase')['intQuantidadeTotalCotasInadimplentesAtivas'].sum().reset_index()

            
            df_totais_por_data = df_totais_por_data.sort_values(by='dtBase')

            
            fig = px.line(df_totais_por_data, 
                        x='dtBase', 
                        y='intQuantidadeTotalCotasInadimplentesAtivas', 
                        markers=True,
                        labels={'intQuantidadeTotalCotasInadimplentesAtivas': 'Quantidade Total de Cotas Inadimplentes', 'dtBase': 'Data Base'},
                        )

            
            st.plotly_chart(fig)
            #-------------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------------
            st.text('1.2.3.2 - Crescimento Percentual e Quantidade de Cotas Inadimplentes em Dezembro por Ano')
            st.text('')
            
            
            df['dtBase'] = pd.to_datetime(df['dtBase'], format='%Y-%m-%d')

            df_dezembro = df[df['dtBase'].dt.month == 12]

            df_dezembro['Ano'] = df_dezembro['dtBase'].dt.year

            df_totais_por_ano_dezembro = df_dezembro.groupby('Ano')['intQuantidadeTotalCotasInadimplentesAtivas'].sum().reset_index()

            df_totais_por_ano_dezembro = df_totais_por_ano_dezembro.sort_values(by='Ano')

            df_totais_por_ano_dezembro['Crescimento (%)'] = df_totais_por_ano_dezembro['intQuantidadeTotalCotasInadimplentesAtivas'].pct_change() * 100

            df_totais_por_ano_dezembro['Crescimento (%)'].fillna(0, inplace=True)

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=df_totais_por_ano_dezembro['Ano'], 
                y=df_totais_por_ano_dezembro['intQuantidadeTotalCotasInadimplentesAtivas'], 
                name='Quantidade de Cotas Ativas (Dezembro)',
                marker_color='rgba(0, 123, 255, 0.6)',
                text=df_totais_por_ano_dezembro['intQuantidadeTotalCotasInadimplentesAtivas'],  # Adicionar rótulo dos valores
                textposition='auto',
                yaxis='y1'
            ))

            fig.add_trace(go.Scatter(
                x=df_totais_por_ano_dezembro['Ano'], 
                y=df_totais_por_ano_dezembro['Crescimento (%)'], 
                name='Crescimento Percentual (%)',
                mode='lines+markers+text',  # Adiciona rótulos aos pontos da linha
                marker_color='rgba(255, 123, 0, 0.8)',
                text=df_totais_por_ano_dezembro['Crescimento (%)'].round(2).astype(str) + '%',  # Rótulo com percentual
                textposition='top center',
                yaxis='y2'
            ))

            fig.update_layout(
                xaxis_title='Ano',
                yaxis=dict(
                    title='Quantidade de Cotas Ativas',
                    titlefont=dict(color='rgba(0, 123, 255, 0.6)'),
                    tickfont=dict(color='rgba(0, 123, 255, 0.6)')
                ),
                yaxis2=dict(
                    title='Crescimento Percentual (%)',
                    titlefont=dict(color='rgba(255, 123, 0, 0.8)'),
                    tickfont=dict(color='rgba(255, 123, 0, 0.8)'),
                    overlaying='y',
                    side='right'
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                )
            )

            st.plotly_chart(fig)
            #-------------------------------------------------------------------------------------------
                       
            st.text('1.2.1.2 - Evoluçãos das Cotas Inadimplentes por Segmento')
            st.text('')
            
            
            #-------------------------------------------------------------------------------------------

            df_totais_por_data = df.groupby(['dtBase', 'strNomeSegmento'])['intQuantidadeTotalCotasInadimplentesAtivas'].sum().reset_index()

            
            df_totais_por_data = df_totais_por_data.sort_values(by='dtBase')

            
            fig = px.line(df_totais_por_data, 
                        x='dtBase', 
                        y='intQuantidadeTotalCotasInadimplentesAtivas', 
                        color='strNomeSegmento',  # Segmentar por cor
                        markers=True,
                        labels={'intQuantidadeTotalCotasInadimplentesAtivas': 'Quantidade Total de Cotas Inadimplentes', 'dtBase': 'Data Base'}
                        )

            
            st.plotly_chart(fig)
            #-------------------------------------------------------------------------------------------
            
            
            
            
            #==============================================================================================================================================================================================================================================
            
            #==============================================================================================================================================================================================================================================
            
            st.subheader('2 - Índice de Cotas Canceladas')
            st.text('')

            st.text('2.1 - Índice de Cotas Canceladas')
            st.text('')

            
            #--------------------------------CARDS GRUPOS ------------------------------------
            col1, col2, col3 = st.columns(3)
            
            col2.metric(label="Índice de Cotas Canceldas", value=formataNumero(mediasSM,0)) 
            
            #--------------------------------------------------------------------------------------------            
            st.text('2.1.1 - Evolução do Índice de Cotas Cancelas')
            st.text('')

            df_totais_por_data = df.groupby(['dtBase', 'strNomeSegmento'])['fltIndiceCotasCanceladas'].sum().reset_index()

            
            df_totais_por_data = df_totais_por_data.sort_values(by='dtBase')

            
            fig = px.line(df_totais_por_data, 
                        x='dtBase', 
                        y='fltIndiceCotasCanceladas', 
                        color='strNomeSegmento',  # Segmentar por cor
                        markers=True,
                        labels={'fltIndiceCotasCanceladas': 'Índice de Cotas Canceladas', 'dtBase': 'Data Base'}
                        )

            
            st.plotly_chart(fig)

            #-------------------------------------------------------------------------------------------
            #==============================================================================================================================================================================================================================================




        #==============================================================================================================================================================================================================================================
            
            
        if administradorasDict[administradoraSelecionada] > 0:
            df = ''
            
            df = getBaseSegmentoMensal(administradorasDict[administradoraSelecionada],segmentosDict[segmentoSelecionado],0)
            
            df['fltValorBem'] = df['intQuantidadeCotasAtivasEmDia'] * df['fltValorMedioBem']
            df['fltValorTotalBem'] = (df['intQuantidadeCotasAtivasEmDia'] + df['intQuantidadeCotasExcluidas'] ) * df['fltValorMedioBem']
            df['dtBase'] = df['dtBase'].apply(pd.to_datetime)
            df = df.sort_values(by='dtBase')
            
            dataMaxima = df['dtBase'].max()

            dfDataMaxima = df[df['dtBase'] == dataMaxima]
            
            
            totais = dfDataMaxima[['fltValorBem','fltValorTotalBem']].sum()       
            medias = dfDataMaxima[['fltTaxaAdministracao', 'intPrazoGrupoMeses', 'fltValorMedioBem']].mean()
            
                 
            
            st.subheader('3 - Valores base consolidada por segmento')
            st.text('')

            st.text('3.1 - Taxas de Administração')
            st.text('')
            
            col1, col2, col3 = st.columns(3)

            col2.metric(label="Taxa Média no Mês", value=formataNumero(medias[0],0))
            
            
            st.text('3.1.1 - Evolução da Taxa de Administração')
            st.text('')
            
            
            #-------------------------------------------------------------------------------------------
            df_totais_por_data = df.groupby('dtBase')['fltTaxaAdministracao'].mean().reset_index()

            
            df_totais_por_data = df_totais_por_data.sort_values(by='dtBase')

            
            fig = px.line(df_totais_por_data, 
                        x='dtBase', 
                        y='fltTaxaAdministracao', 
                        markers=True,
                        labels={'fltTaxaAdministracao': 'Taxa de Administração Média', 'dtBase': 'Data Base'},
                        )

            
            st.plotly_chart(fig)
            #-------------------------------------------------------------------------------------------            
            
            st.text('3.1.2 - Evolução da Taxa de Administração por Segmento')
            st.text('')
            
            #-------------------------------------------------------------------------------------------            
            df_totais_por_data = df.groupby(['dtBase', 'strNomeSegmento'])['fltTaxaAdministracao'].mean().reset_index()

            
            df_totais_por_data = df_totais_por_data.sort_values(by='dtBase')

            
            fig = px.line(df_totais_por_data, 
                        x='dtBase', 
                        y='fltTaxaAdministracao', 
                        color='strNomeSegmento',  # Segmentar por cor
                        markers=True,
                        labels={'fltTaxaAdministracao': 'Taxa de Administração Média', 'dtBase': 'Data Base'}
                        )

            
            st.plotly_chart(fig)            
            #-------------------------------------------------------------------------------------------            
            
            st.text('3.2 - Valores dos Bens')
            st.text('')
            
            col1, col2, col3, col4 = st.columns(4)

            
            col2.metric(label="Valor Total Bem", value=formataNumero(totais[0],0))
            col3.metric(label="Valor Médio Bem", value=formataNumero(medias[2],0))
            
            #-------------------------------------------------------------------------------------------            

            st.text('3.2.1 - Evolução Valor do Bem (Trmestralmente)')
            st.text('')
            
            df['Mes'] = pd.to_datetime(df['dtBase']).dt.month
            df_filtrado = df[df['Mes'].isin([3, 6, 9, 12])]
            
            df_totais_por_data = df_filtrado.groupby('dtBase')['fltValorBem'].sum().reset_index()

            
            df_totais_por_data = df_totais_por_data.sort_values(by='dtBase')

            fig = px.line(df_totais_por_data, 
                        x='dtBase', 
                        y='fltValorBem', 
                        markers=True,
                        labels={'fltValorBem': 'Valor Total do Bem', 'dtBase': 'Data Base'},
                        )

            st.plotly_chart(fig)            
            
            
            #-------------------------------------------------------------------------------------------            

            #-------------------------------------------------------------------------------------------            

            st.text('3.2.2 - Evolução Valor Médio do Bem (Trimestralmente)')
            st.text('')
            
            df['Mes'] = pd.to_datetime(df['dtBase']).dt.month
            df_filtrado = df[df['Mes'].isin([3, 6, 9, 12])]

            df_totais_por_data = df_filtrado.groupby('dtBase')['fltValorMedioBem'].mean().reset_index()

            
            df_totais_por_data = df_totais_por_data.sort_values(by='dtBase')

            fig = px.line(df_totais_por_data, 
                        x='dtBase', 
                        y='fltValorMedioBem', 
                        markers=True,
                        labels={'fltValorMedioBem': 'Valor Médio do Bem', 'dtBase': 'Data Base'},
                        )

            st.plotly_chart(fig)            
            
            
            #-------------------------------------------------------------------------------------------            
            
                        
                        
            st.text('3.2.3 - Valor Total do Bem por Segmento')
            st.text('')
            
            #-------------------------------------------------------------------------------------------            
            df_totais_por_data = df.groupby(['dtBase', 'strNomeSegmento'])['fltValorMedioBem'].sum().reset_index()

            
            df_totais_por_data = df_totais_por_data.sort_values(by='dtBase')

            
            fig = px.line(df_totais_por_data, 
                        x='dtBase', 
                        y='fltValorMedioBem', 
                        color='strNomeSegmento',  # Segmentar por cor
                        markers=True,
                        labels={'fltValorMedioBem': 'Valor Total Bem', 'dtBase': 'Data Base'}
                        )

            
            st.plotly_chart(fig)            
            #-------------------------------------------------------------------------------------------            


            st.text('3.2.4 - Valor Médio do Bem por Segmento')
            st.text('')
            
            #-------------------------------------------------------------------------------------------            
            df_totais_por_data = df.groupby(['dtBase', 'strNomeSegmento'])['fltValorMedioBem'].mean().reset_index()

            
            df_totais_por_data = df_totais_por_data.sort_values(by='dtBase')

            
            fig = px.line(df_totais_por_data, 
                        x='dtBase', 
                        y='fltValorMedioBem', 
                        color='strNomeSegmento',  # Segmentar por cor
                        markers=True,
                        labels={'fltValorMedioBem': 'Valor Médio Bem', 'dtBase': 'Data Base'}
                        )

            
            st.plotly_chart(fig)            
            #-------------------------------------------------------------------------------------------            
                        
            #-------------------------------------------------------------------------------------------
            st.text('3.2.5 - Crescimento Percentual e Valor Total do Bem em Dezembro por Ano')
            st.text('')
            
            
            df['dtBase'] = pd.to_datetime(df['dtBase'], format='%Y-%m-%d')

            df_dezembro = df[df['dtBase'].dt.month == 12]

            df_dezembro['Ano'] = df_dezembro['dtBase'].dt.year

            df_totais_por_ano_dezembro = df_dezembro.groupby('Ano')['fltValorMedioBem'].sum().reset_index()

            df_totais_por_ano_dezembro = df_totais_por_ano_dezembro.sort_values(by='Ano')

            df_totais_por_ano_dezembro['Crescimento (%)'] = df_totais_por_ano_dezembro['fltValorMedioBem'].pct_change() * 100

            df_totais_por_ano_dezembro['Crescimento (%)'].fillna(0, inplace=True)

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=df_totais_por_ano_dezembro['Ano'], 
                y=df_totais_por_ano_dezembro['fltValorMedioBem'], 
                name='Quantidade de Cotas Ativas (Dezembro)',
                marker_color='rgba(0, 123, 255, 0.6)',
                text=df_totais_por_ano_dezembro['fltValorMedioBem'],  # Adicionar rótulo dos valores
                textposition='auto',
                yaxis='y1'
            ))

            fig.add_trace(go.Scatter(
                x=df_totais_por_ano_dezembro['Ano'], 
                y=df_totais_por_ano_dezembro['Crescimento (%)'], 
                name='Crescimento Percentual (%)',
                mode='lines+markers+text',  # Adiciona rótulos aos pontos da linha
                marker_color='rgba(255, 123, 0, 0.8)',
                text=df_totais_por_ano_dezembro['Crescimento (%)'].round(2).astype(str) + '%',  # Rótulo com percentual
                textposition='top center',
                yaxis='y2'
            ))

            fig.update_layout(
                xaxis_title='Ano',
                yaxis=dict(
                    title='Quantidade de Cotas Ativas',
                    titlefont=dict(color='rgba(0, 123, 255, 0.6)'),
                    tickfont=dict(color='rgba(0, 123, 255, 0.6)')
                ),
                yaxis2=dict(
                    title='Crescimento Percentual (%)',
                    titlefont=dict(color='rgba(255, 123, 0, 0.8)'),
                    tickfont=dict(color='rgba(255, 123, 0, 0.8)'),
                    overlaying='y',
                    side='right'
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                )
            )

            st.plotly_chart(fig)
            #-------------------------------------------------------------------------------------------                        
            #==============================================================================================================================================================================================================================================

            df = getBaseContabil(administradorasDict[administradoraSelecionada],segmentosDict[segmentoSelecionado],0)
            
            df['fltResultado'] = df['fltReceitaOperacional'] + df['fltReceitaNaoOperacional'] + df['fltDespesaOperacional'] + df['fltDespesaNaoOperacional']
            df['fltIndiceDASobreReceita'] = -(df['fltDespesaAdministrativa'] / (df['fltReceitaOperacional']+df['fltReceitaNaoOperacional']))
            df['fltIndiceDOSemDASobreReceita'] = -(df['fltDespesaOperacional'] - df['fltDespesaAdministrativa'])/(df['fltReceitaOperacional'] + df['fltReceitaNaoOperacional'])
            df['fltIndiceDOSobreReceita'] = -(df['fltDespesaOperacional'] / (df['fltReceitaOperacional'] + df['fltReceitaNaoOperacional']))
            df['fltIndiceResultadoSobreReceita'] = df['fltResultado'] / (df['fltReceitaOperacional'] + df['fltReceitaNaoOperacional'])
            
            
            df['dtBase'] = df['dtBase'].apply(pd.to_datetime)
            df = df.sort_values(by='dtBase')
            
            

            dataMaxima = df['dtBase'].max()
            dfDataMaxima = df[df['dtBase'] == dataMaxima]
            
            
            
            #-------------------------------------------------------------------------------------------                        


            st.subheader('4 - Valores Base Contábil')
            st.text('')

            st.text('4.1 - Valores Contas Contábeis')
            st.text('')

            
            #--------------------------------CARDS GRUPOS ------------------------------------
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            col1.metric(label="Receita Operacional", value=formataNumero(dfDataMaxima['fltReceitaOperacional'].values[0],0)) 
            col2.metric(label="Receita Não Opercional", value=formataNumero(dfDataMaxima['fltReceitaNaoOperacional'].values[0],0)) 
            col3.metric(label="Despesa Operacional", value=formataNumero(dfDataMaxima['fltDespesaOperacional'].values[0],0)) 
            col4.metric(label="Despesa Administrativa", value=formataNumero(dfDataMaxima['fltDespesaAdministrativa'].values[0],0)) 
            col5.metric(label="Despesa Não Operacional", value=formataNumero(dfDataMaxima['fltDespesaNaoOperacional'].values[0],0)) 
            col6.metric(label="Resultado", value=formataNumero(dfDataMaxima['fltResultado'].values[0],0)) 
            st.text('')
            #-------------------------------------------------------------------------------------------                        
            
            
            
            #-------------------------------------------------------------------------------------------                        
            st.text('4.1.1 - Evolução Contas Contábeis')
            st.text('')
            
            fig = go.Figure()

            cores = ['rgba(0, 123, 255, 0.5)',
                    'rgba(255, 165, 0, 0.5)', 
                    'rgba(0, 255, 0, 0.5)',
                    'rgba(255, 0, 0, 0.5)',
                    'rgba(0, 255, 255, 0.8)',
                    ]  

            for i, col in enumerate(['fltReceitaOperacional', 'fltReceitaNaoOperacional', 'fltDespesaOperacional', 'fltDespesaNaoOperacional', 'fltResultado']):
                fig.add_trace(go.Scatter(
                    x=df['dtBase'].dt.strftime('%Y-%m'),  # Formato da data
                    y=df[col],
                    mode='lines+markers',  # Usar apenas linhas com marcadores
                    name=col,
                    line=dict(color=cores[i], width=2),  # Cor da linha
                    marker=dict(color=cores[i], size=8),  # Cor e tamanho dos marcadores
                    hoverinfo='y+name'  # Informações ao passar o mouse
                ))

            fig.update_layout(
                title='Evolução das Contas Contábeis e Resultado',
                xaxis_title='Mês/Ano',
                yaxis_title='Valores',
                legend=dict(title='Colunas'),
                template='plotly_white'
            )

            st.plotly_chart(fig) 
            
            #-------------------------------------------------------------------------------------------
            st.text('4.1.2 - Crescimento Percentual e Valor Total do Resultado por Semestre')
            st.text('')
            
            
            df['dtBase'] = pd.to_datetime(df['dtBase'], format='%Y-%m-%d')

            df['Ano'] = df['dtBase'].dt.year
            df['Mês'] = df['dtBase'].dt.month

            df_totais_por_mes = df.groupby(['Ano', 'Mês'])['fltResultado'].sum().reset_index()

            df_totais_por_mes['Mês_Ano'] = df_totais_por_mes['Mês'].astype(str) + '/' + df_totais_por_mes['Ano'].astype(str)

            df_totais_por_mes['Crescimento (%)'] = df_totais_por_mes['fltResultado'].pct_change() * 100

            df_totais_por_mes['Crescimento (%)'].fillna(0, inplace=True)

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=df_totais_por_mes['Mês_Ano'],
                y=df_totais_por_mes['fltResultado'],
                name='Resultado',
                marker_color='rgba(0, 123, 255, 0.6)',
                textfont=dict(color='rgba(0, 255, 255, 1)'),
                text=df_totais_por_mes['fltResultado'],
                texttemplate='%{y:,.2f}',
                textposition='auto',
                yaxis='y1'
            ))

            fig.add_trace(go.Scatter(
                x=df_totais_por_mes['Mês_Ano'],
                y=df_totais_por_mes['Crescimento (%)'],
                name='Crescimento Percentual (%)',
                mode='lines+markers+text',  
                marker_color='rgba(255, 123, 0, 0.8)',
                text=df_totais_por_mes['Crescimento (%)'].round(2).astype(str) + '%',  
                textposition='top center',
                yaxis='y2'
            ))

            
            fig.update_layout(
                xaxis_title='Mês/Ano',
                yaxis=dict(
                    title='Resultado',
                    titlefont=dict(color='rgba(0, 123, 255, 0.6)'),
                    tickfont=dict(color='rgba(0, 123, 255, 0.6)')
                ),
                yaxis2=dict(
                    title='Crescimento Percentual (%)',
                    titlefont=dict(color='rgba(255, 123, 0, 0.8)'),
                    tickfont=dict(color='rgba(255, 123, 0, 0.8)'),
                    overlaying='y',
                    side='right'
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                )
            )

            
            st.plotly_chart(fig)
            #-------------------------------------------------------------------------------------------                        
            
                        

            st.text('4.2 - Índices Contábeis')
            st.text('')

            
            #--------------------------------CARDS GRUPOS ------------------------------------
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            col1.metric(label="Índice DA Sobre Receita", value=formataNumero(dfDataMaxima['fltIndiceDASobreReceita'].values[0],0)) 
            col2.metric(label="Índice DO Sobre Receita", value=formataNumero(dfDataMaxima['fltIndiceDOSemDASobreReceita'].values[0],0)) 
            col3.metric(label="Índice DO Sobre Receita sem DA", value=formataNumero(dfDataMaxima['fltIndiceDOSobreReceita'].values[0],0)) 
            col4.metric(label="Índice Resultado Sobre Receita", value=formataNumero(dfDataMaxima['fltIndiceResultadoSobreReceita'].values[0],0)) 
            st.text('')
            #-------------------------------------------------------------------------------------------                                    
            
            st.text('4.2.2 - Evolução dos Índices Contábeis')
            st.text('')
            
            fig = go.Figure()

            cores = ['rgba(0, 123, 255, 0.5)',
                    'rgba(255, 165, 0, 0.5)', 
                    'rgba(0, 255, 0, 0.5)',
                    'rgba(255, 0, 0, 0.5)',
                    ]  

            for i, col in enumerate(['fltIndiceDASobreReceita', 'fltIndiceDOSemDASobreReceita', 'fltIndiceDOSobreReceita', 'fltIndiceResultadoSobreReceita']):
                fig.add_trace(go.Scatter(
                    x=df['dtBase'].dt.strftime('%Y-%m'),  # Formato da data
                    y=df[col],
                    mode='lines+markers',  # Usar apenas linhas com marcadores
                    name=col,
                    line=dict(color=cores[i], width=2),  # Cor da linha
                    marker=dict(color=cores[i], size=8),  # Cor e tamanho dos marcadores
                    hoverinfo='y+name'  # Informações ao passar o mouse
                ))

            fig.update_layout(
                title='Evolução dos Índices Contábeis',
                xaxis_title='Mês/Ano',
                yaxis_title='Valores',
                legend=dict(title='Colunas'),
                template='plotly_white'
            )

            st.plotly_chart(fig) 
            
            #-------------------------------------------------------------------------------------------
            
            #==============================================================================================================================================================================================================================================            
            
            

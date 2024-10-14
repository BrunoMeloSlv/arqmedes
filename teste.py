import streamlit as st
import pandas as pd
import numpy as np


def show():
    try:
        # Carrega os dados
        #dados = pd.read_csv('https://raw.githubusercontent.com/BrunoMeloSlv/arqmedes/refs/heads/main/dados.csv', sep = ',')
        dados = pd.read_csv("data_export_20241011.csv", sep=",")
        max = '2024-06-01'
        dados = dados[dados['dtBase'] == max]

        dados.rename(columns={
            'idAdministradora': 'Administradora',
            'strCnpjAdministradora': 'CNPJ',
            'strNomeAdministradora': 'Nome Administradora',
            'idTipoAdministradora': 'Tipo Administradora ID',
            'NomeTipoAdministradora': 'Tipo Administradora',
            'idSegmento': 'Segmento ID',
            'strNomeSegmento': 'Segmento',
            'dtBase': 'Data Base',
            'fltTaxaAdministracao': 'Taxa de Administração',
            'intQuantidadeGruposAtivos': 'Grupos Ativos',
            'intQuantidadeGruposConstituidosMes': 'Grupos Constituidos no Mês',
            'intQuantidadeGruposEncerradosMes': 'Grupos Encerrados no Mês',
            'intQuantidadeCotasComercializadasMes': 'Cotas Comercializadas no Mês',
            'intQuantidadeCotasExcluidasComercializar': 'Cotas Excluídas de Comercialização',
            'intQuantidadeAcumuladaCotasAtivasContempladas': 'Cotas Ativas Contempladas Acumuladas',
            'intQuantidadeCotasAtivasNaoContempladas': 'Cotas Ativas Não Contempladas',
            'intQuantidadeCotasAtivasContempladasMes': 'Cotas Ativas Contempladas no Mês',
            'intQuantidadeCotasAtivasAdimplentes': 'Cotas Ativas Adimplentes',
            'intQuantidadeCotasAtivasContempladasInadimplente': 'Cotas Contempladas Inadimplentes',
            'intQuantidadeCotasAtivasNaoContempladasInadimplentes': 'Cotas Não Contempladas Inadimplentes',
            'intQuantidadeCotasExcluidas': 'Cotas Excluídas',
            'intQuantidadeCotasAtivasQuitadas': 'Cotas Ativas Quitadas',
            'intQuantidadeCotasAtivasComCreditoPendenteUtilizacao': 'Cotas com Crédito Pendente',
            'fltReceitaOperacional': 'Receita Operacional',
            'fltReceitaNaoOperacional': 'Receita Não Operacional',
            'fltDespesaOperacional': 'Despesa Operacional',
            'fltDespesaAdministrativa': 'Despesa Administrativa',
            'fltDespesaNaoOperacional': 'Despesa Não Operacional',
            'fltResultado': 'Resultado',
            'fltIndiceDASobreReceita': 'Índice DA Sobre Receita',
            'fltIndiceDOSemDASobreReceita': 'Índice DO Sem DA Sobre Receita',
            'fltIndiceDOSobreReceita': 'Índice DO Sobre Receita',
            'fltIndiceResultadoSobreReceita': 'Índice Resultado Sobre Receita',
            'fltIndiceCotaCancelada': 'Índice de Cotas Canceladas',
            'intTotalCotasAtivas':'Total Cotas Ativas (calc)',
            'intTotalCotasInadimplentes':'Total Cotas Inadimplentes (calc)'
        }, inplace=True)
    
        # Função MelhoresEscolhas
        def MelhoresEscolhas(data, positivo, negativo, empresas):
            df = data.drop(columns=[empresas])
            
            # Seleciona as colunas positivas e negativas
            positivos = df[list(positivo)]
            negativos = df[list(negativo)]

            def ahp_positivos(tabela):
                table = []
                for i in tabela.columns:
                    total = sum(tabela[i])  # Calcula o total da coluna
                    a = np.where(total == 0, 0, tabela[i] / total)  # Normalização da coluna
                    table.append(a)
                table = pd.DataFrame(table).T
                table.columns = tabela.columns
                return table

            positivos = ahp_positivos(positivos)

            def numeros_negativos(tabela):
                table = []
                for i in tabela.columns:
                    a = np.where(tabela[i] == 0, 0, 1 / tabela[i])  # Inversão dos valores
                    table.append(a)
                table = pd.DataFrame(table).T
                tab_final = []
                for i in table.columns:
                    total = table[i].sum()
                    b = np.where(total == 0, 0, table[i] / total)  # Normalização pelo total da coluna
                    tab_final.append(b)
                tab_final = pd.DataFrame(tab_final).T
                tab_final.columns = tabela.columns
                return tab_final

            negativos = numeros_negativos(negativos)
            tabela_ahp = pd.concat([positivos, negativos], axis=1)

            medias = pd.DataFrame(tabela_ahp.mean(), columns=['media'])
            desvio = pd.DataFrame(tabela_ahp.std(), columns=['desvio'])
            fator_ahp = pd.concat([medias, desvio], axis=1)
            fator_ahp['desvio'] = fator_ahp['desvio'].fillna(np.mean(fator_ahp['desvio']))
            fator_ahp['desvio/media'] = fator_ahp['desvio'] / fator_ahp['media']
            fator_ahp['Fator'] = fator_ahp['desvio/media'] / sum(fator_ahp['desvio/media'])

            fator = pd.DataFrame(fator_ahp['Fator']).T
            colunas_para_calculo = fator.columns

            def matriz_de_decisao(tabela, fator):
                table = []
                for i in colunas_para_calculo:
                    a = tabela[i] * fator[i][0]
                    table.append(a)
                table = pd.DataFrame(table).T
                return table

            resultado_ahp = matriz_de_decisao(tabela_ahp, fator)
            soma = resultado_ahp.sum(axis=1)
            soma = pd.DataFrame(soma, columns=['Resultado'])

            # Redefinir o índice após a soma para garantir que ele não se desalinhe
            soma = soma.reset_index(drop=True)

            # Mesclar com a coluna de empresas, redefinindo o índice
            melhores_escolhas = pd.concat([soma, data[[empresas]].reset_index(drop=True)], axis=1)

            # Ordenar os resultados pelo valor do resultado e redefinir o índice novamente
            melhores_escolhas = melhores_escolhas.sort_values(by='Resultado', ascending=False).reset_index(drop=True)

            # Renomeia a coluna de empresas, se necessário
            melhores_escolhas.rename(columns={empresas: 'Empresa'}, inplace=True)

            return melhores_escolhas, fator.T

        # Aplicação Streamlit
        import streamlit as st
        import pandas as pd

        # Supõe-se que os dados já estão carregados no DataFrame 'dados'

        st.title('Seleção de Colunas Positivas e Negativas para Análise AHP Gaussiano')

        # Lista de colunas disponíveis
        dados.drop(columns=['Administradora','CNPJ','Tipo Administradora ID','Segmento ID'], inplace= True)

        df= dados.drop(columns=[
            'Tipo Administradora',
            'Nome Administradora',
            'Data Base',
            'Segmento'
        ])



        colunas_disponiveis = list(df.columns)

        # Adicionar os filtros na barra lateral (sidebar)
        st.sidebar.header('Filtros')
        st.sidebar.text('Data de atualização 01/06/2024')

        # Selecionar a coluna de empresas
        coluna_empresas = 'Nome Administradora'  # Coluna fixa de empresas

        # Selecionar tipo adm
        tipo_administradoras = ['Todos'] + list(dados['Tipo Administradora'].unique())
        tipo_administradora = st.sidebar.selectbox('Selecione o Tipo de Administradora:', tipo_administradoras)

        # Selecionar tipo segmento
        segmentos = ['Todos'] + list(dados['Segmento'].unique())
        segmento = st.sidebar.selectbox('Selecione o Segmento:', segmentos)

        # Aplicar os dois filtros principais de tipo administradora e segmento
        if tipo_administradora != 'Todos' and segmento != 'Todos':
            dados_filtrados = dados[
                (dados['Tipo Administradora'] == tipo_administradora) & 
                (dados['Segmento'] == segmento)
            ].reset_index(drop=True)
        elif tipo_administradora != 'Todos':
            dados_filtrados = dados[
                (dados['Tipo Administradora'] == tipo_administradora)
            ].reset_index(drop=True)
        elif segmento != 'Todos':
            dados_filtrados = dados[
                (dados['Segmento'] == segmento)
            ].reset_index(drop=True)
        else:
            dados_filtrados = dados.reset_index(drop=True)


        # Selecionar colunas positivas
        colunas_positivas = st.sidebar.multiselect('Selecione as colunas positivas:', colunas_disponiveis)

        # Selecionar colunas negativas
        colunas_negativas = st.sidebar.multiselect('Selecione as colunas negativas:', colunas_disponiveis)

        # Número de filtros a serem aplicados
        num_filtros = st.sidebar.number_input('Quantos filtros deseja aplicar?', min_value=1, max_value=10, step=1)

        filtros = []
        # Criar a interface para múltiplos filtros
        for i in range(int(num_filtros)):
            st.sidebar.write(f"Filtro {i+1}")
            coluna_filtro = st.sidebar.selectbox(f'Selecione a coluna para o Filtro {i+1}:', colunas_disponiveis, key=f"coluna_filtro_{i}")
            
            # Selecionar o tipo de condição
            condicao = st.sidebar.selectbox(f'Selecione a condição para o Filtro {i+1}:', ['Igual a', 'Maior ou igual a', 'Menor ou igual a'], key=f"condicao_{i}")
            
            # Selecionar o valor do filtro
            valor_filtro = st.sidebar.text_input(f'Digite o valor para o Filtro {i+1}:', key=f"valor_filtro_{i}")
            
            filtros.append((coluna_filtro, condicao, valor_filtro))

        # Aplicar os filtros selecionados
        for coluna_filtro, condicao, valor_filtro in filtros:
            if valor_filtro:
                # Tentar converter o valor do filtro em float
                try:
                    # Verifica se a coluna é numérica
                    if pd.api.types.is_numeric_dtype(dados[coluna_filtro]):
                        valor_filtro = float(valor_filtro)
                        
                        if condicao == 'Igual a':
                            dados_filtrados = dados_filtrados[dados_filtrados[coluna_filtro] == valor_filtro]
                        elif condicao == 'Maior ou igual a':
                            dados_filtrados = dados_filtrados[dados_filtrados[coluna_filtro] >= valor_filtro]
                        elif condicao == 'Menor ou igual a':
                            dados_filtrados = dados_filtrados[dados_filtrados[coluna_filtro] <= valor_filtro]
                    else:
                        # Se não for numérica, compara como string
                        if condicao == 'Igual a':
                            dados_filtrados = dados_filtrados[dados_filtrados[coluna_filtro] == valor_filtro]
                except ValueError:
                    st.warning(f"Valor '{valor_filtro}' não é um número válido para a coluna '{coluna_filtro}'.")

        # Exibir os dados filtrados
        with st.expander("Dados após aplicação dos filtros"):
            st.dataframe(dados_filtrados)

        # Verifica se o usuário selecionou colunas suficientes
        if len(colunas_positivas) > 0 and len(colunas_negativas) > 0 and coluna_empresas:
            st.write("Executando a análise AHP com os dados filtrados...")
            resultado, fator = MelhoresEscolhas(dados_filtrados, colunas_positivas, colunas_negativas, coluna_empresas)

            # Exibe o resultado
            st.write("Melhores escolhas baseadas na análise AHP:")
            st.dataframe(resultado)

            # Exibe o fator calculado
            st.write("Fatores calculados:")
            st.dataframe(fator)
        else:
            st.write("Por favor, selecione pelo menos uma coluna positiva, uma negativa e a coluna de empresas.")
    
    except FileNotFoundError:
        st.error("O arquivo 'data_export_20241011.csv' não foi encontrado.")
    except pd.errors.EmptyDataError:
        st.error("O arquivo CSV está vazio.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados: {e}")            
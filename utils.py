import pandas as pd
from conexao import get_connection

def getAdministradora():
    engine = get_connection()
    query = "SELECT idAdministradora, strNomeAdministradora FROM Administradora"
    administradoras = pd.read_sql(query, engine)
    
    return administradoras


def getSegmento():
    engine = get_connection()
    query = "SELECT idSegmento, strNomeSegmento FROM Segmento"
    segmentos = pd.read_sql(query, engine)
    
    return segmentos


def getBaseConsolidadaSegmentoMensal(idAdministradora, idSegmento, dtBase):
    engine = get_connection()
    query = f'''
                    SELECT 
                    a.idAdministradora,
                    a.strCnpjAdministradora,
                    a.strNomeAdministradora,
                    bcm.idSegmento,
                    s.strNomeSegmento,
                    bcm.dtBase,
                    bcm.fltTaxaAdministracao,
                    bcm.intQuantidadeGruposAtivos,
                    bcm.intQuantidadeGruposConstituidosMes,
                    bcm.intQuantidadeGruposEncerradosMes,
                    bcm.intQuantidadeCotasComercializadasMes,
                    bcm.intQuantidadeCotasExcluidasComercializar,
                    bcm.intQuantidadeAcumuladaCotasAtivasContempladas,
                    bcm.intQuantidadeCotasAtivasNaoContempladas,
                    bcm.intQuantidadeCotasAtivasContempladasMes,
                    bcm.intQuantidadeCotasAtivasAdimplentes,
                    bcm.intQuantidadeCotasAtivasContempladasInadimplente,
                    bcm.intQuantidadeCotasAtivasNaoContempladasInadimplentes,
                    bcm.intQuantidadeCotasExcluidas,
                    bcm.intQuantidadeCotasAtivasQuitadas,
                    bcm.intQuantidadeCotasAtivasComCreditoPendenteUtilizacao
                FROM 
                    Administradora a
                INNER JOIN 
                    BaseConsolidadaSegmentoMensal bcm ON a.idAdministradora = bcm.idAdministradora
                INNER JOIN 
                    Segmento s ON bcm.idSegmento = s.idSegmento '''
    
    
    adm =''
    seg =''
                    
    if idAdministradora > 0:
        adm = f'WHERE a.idAdministradora = {idAdministradora}'
        query = query + ' ' + adm
        
    
    if idSegmento > 0:
        seg = f'and s.idSegmento = {idSegmento}'
        query = query + ' ' + seg
        
    if idAdministradora > 0:    
        BaseConsolidadaSegmentoMensal = pd.read_sql(query, engine)
    
    return BaseConsolidadaSegmentoMensal
    
    
def formataNumero(numero, tipo):
    
    if tipo == 0:
        numeroFormatado = f'{numero:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    elif tipo ==1:
        numeroFormatado = f'{numero:,.0f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    return numeroFormatado

def formataData(data):
    dataFormata = data.strftime('%d/%m/%Y')
    return dataFormata


def getBaseSegmentoMensal(idAdministradora, idSegmento, dtBase):
    engine = get_connection()
    query = f'''
                    SELECT 
                    a.idAdministradora,
                    a.strCnpjAdministradora,
                    a.strNomeAdministradora,
                    bcm.idSegmento,
                    s.strNomeSegmento,
                    bcm.dtBase,
                    bcm.fltTaxaAdministracao,
					bcm.idIndiceCorrecao,
					bcm.strCodigoGrupo,
					bcm.strCodigoAssembleiaGeralOrdinaria,
					bcm.fltValorMedioBem,
					bcm.intPrazoGrupoMeses,
					bcm.intQuantidadeCotasAtivasEmDia,
					bcm.intQuantidadeCotasAtivasContempladasInadimplentes,
					bcm.intQuantidadeCotasAtivasNaoContempladasInadimplentes,
					bcm.intQuantidadeCotasAtivasContempladasMes,
					bcm.intQuantidadeCotasExcluidas,
					bcm.intQuantidadeCotasAtivasQuitadas,
					bcm.intQuantidadeCotasAtivasCreditoPedenteUtilizacao
                FROM 
                    Administradora a
                INNER JOIN 
                    BaseConsolidadaMensal bcm ON a.idAdministradora = bcm.idAdministradora
                INNER JOIN 
                    Segmento s ON bcm.idSegmento = s.idSegmento '''
    
    
    adm =''
    seg =''
                    
    if idAdministradora > 0:
        adm = f'WHERE a.idAdministradora = {idAdministradora}'
        query = query + ' ' + adm
        
    
    if idSegmento > 0:
        seg = f'and s.idSegmento = {idSegmento}'
        query = query + ' ' + seg
        
    if idAdministradora > 0:    
        BaseSegmentoMensal = pd.read_sql(query, engine)
    
    return BaseSegmentoMensal

def getBaseContabil(idAdministradora, idSegmento, dtBase):
    engine = get_connection()
    query = f'''
                SELECT 
                    a.idAdministradora,
                    a.strCnpjAdministradora,
                    a.strNomeAdministradora,
                    ta.idTipoAdministradora,
                    ta.NomeTipoAdministradora,
                    bc.dtBase,
                    SUM(CASE WHEN strNumeroConta = '71000008' THEN fltSaldoConta ELSE 0 END) AS fltReceitaOperacional,
                    SUM(CASE WHEN strNumeroConta = '73000006' THEN fltSaldoConta ELSE 0 END) AS fltReceitaNaoOperacional,
                    SUM(CASE WHEN strNumeroConta = '81000005' THEN fltSaldoConta ELSE 0 END) AS fltDespesaOperacional,
                    SUM(CASE WHEN strNumeroConta = '81700006' THEN fltSaldoConta ELSE 0 END) AS fltDespesaAdministrativa,
                    SUM(CASE WHEN strNumeroConta = '83000003' THEN fltSaldoConta ELSE 0 END) AS fltDespesaNaoOperacional
                FROM BaseContabil bc
                INNER JOIN  Administradora a ON bc.idAdministradora = a.idAdministradora 
                INNER JOIN	TipoAdministradora ta ON a.idTipoAdministradora = ta.idTipoAdministradora
                WHERE strNumeroConta IN ('71000008', '73000006', '81000005', '81700006', '83000003')
                AND MONTH(dtBase) IN (6, 12)
                '''
        
    adm =''
    seg =''
                    
    if idAdministradora > 0:
        adm = f'and a.idAdministradora = {idAdministradora}'
        query = query + ' ' + adm
        
    
    if idSegmento > 0:
        seg = f'and s.idSegmento = {idSegmento}'
        query = query + ' ' + seg
        
    query = query + '''    GROUP BY     a.idAdministradora,
                    a.strCnpjAdministradora,
                    a.strNomeAdministradora,
                    ta.idTipoAdministradora,
                    ta.NomeTipoAdministradora,
                    bc.dtBase '''
        
    if idAdministradora > 0:    
        BaseSegmentoMensal = pd.read_sql(query, engine)
    
    return BaseSegmentoMensal

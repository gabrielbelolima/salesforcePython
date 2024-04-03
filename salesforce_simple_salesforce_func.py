# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 09:16:18 2023

@author: gabriel.lima
"""

from simple_salesforce import Salesforce
from login_params import login_params #I recommend you use enviroment secrets! 
import requests
import pandas as pd
from tqdm.notebook import tqdm   

# auth               
sc_sfuser = login_params['email']
sc_sfpassword = login_params['password']
sc_sftoken = login_params['securityToken']
domain = login_params['domain.my']

def session_sf(sc_sfuser=sc_sfuser, sc_sfpassword=sc_sfpassword, sc_sftoken=sc_sftoken, domain=domain):
    
  session = requests.Session()
  sf = Salesforce(username=sc_sfuser, 
                  password=sc_sfpassword, 
                  security_token=sc_sftoken,
                  domain=domain,
                  session=session
                )
  return sf

sf = session_sf()

def get_query(query = str(), attributes = False):
    '''
    Executa Query SOQL numa determinada versão da API
    input: Query SOQL, url de ação, versão desejada e json de autenticação.
    output: json com a resposta da query, link para apróxima iteração e metadados da query 
    
    OBS.: Response sem paginação!
    '''        
    
    data = sf.query_all(query)
    df = pd.DataFrame(data['records'])
    
    if attributes == False:
        return df.drop('attributes', axis = 1)  
    else:
        return df
    
    
def get_label(table_name =str(), return_df = False):
    '''Recebe o nome de um objeto do salesforce e retorna label_name's cadastradas no sistema'''

    # get columns' labels
    query_label = "SELECT Id, Label, QualifiedApiName, DataType FROM FieldDefinition Where EntityDefinition.QualifiedApiName='{}'".format(table_name)
    
    label_conta = get_query(query_label)

    dict_label = label_conta[['QualifiedApiName','Label']].set_index('QualifiedApiName').to_dict()['Label']

    label_index = label_conta.reset_index().reset_index().groupby('Label', as_index=False)[['index','Label']].agg(list)
    label_index['Label_index'] = label_index['Label'].apply(lambda x: [i[0]+str(i[1][0]+1) if i[1][0] > 0 else i[0] for i in zip(x, enumerate(x))])
    c1 = label_index[['index']].explode('index').reset_index(drop = True)
    c2 = label_index[['Label_index']].explode('Label_index').reset_index(drop = True)
    label_index = c1.join(c2).sort_values('index').set_index('index')

    label_conta = label_conta.join(label_index)
    label_conta = label_conta[['Id','Label','Label_index','QualifiedApiName','DataType']]

    dict_label = label_conta[['QualifiedApiName','Label_index']].set_index('QualifiedApiName').to_dict()['Label_index']
    
    if return_df == True:
        return label_conta
    
    return dict_label 


def list_to_string(ls_col = str()):
    '''Recebe uma lista de colunas e retorna um string para ser utilizado em queries SQL'''
    s = ''
    for c in ls_col:
        s += c+', '
    
    return s


def get_columns(tb_name = str()):
    '''List all columns from table'''
    ls_col = get_query("SELECT FIELDS(ALL) FROM {} LIMIT 1".format(tb_name)).columns
    
    return str(list(ls_col)).replace('[','').replace(']','').replace("'",'')


def get_table(table_name, where = None, limit = None, label = True, bar = True):
    '''
    Recebe table_name e retorna todos os campos do objeto do salesforce
    '''
    # Cria Query 1 - Pegar nome das colunas
    #table_name = 'RecordType'

    # Lista de Colunas do objeto 
    ls_columns = get_columns(table_name)

    # Cria query
    q1 = "SELECT  {0} FROM {1}".format(ls_columns, table_name) # Passa colunas na query

    if where != None:
        q1 = q1+ " WHERE {}".format(where)
    if limit!= None:
        q1 = q1+" LIMIT {}".format(limit)
    
    # Generator com os dados da query
    data = sf.query_all_iter(q1)

    # totalSize
    totalSize = sf.query(q1)['totalSize']
    if totalSize == 0:
        return print('\nA query não retornou resultados no Salesforce!\ntotalSize = 0\n\nquery: {}'.format(q1))
    
    
    # loop para criar dataFrame com dados do generator usando tqdm:
    df = None
    
    if bar == True:
        range_aux = tqdm(range(totalSize), leave=False)
    else:
        range_aux = range(totalSize)
        
    df = pd.concat(
            [pd.DataFrame(next(data)).iloc[[1]] for x in range_aux], 
            ignore_index=True
        )
    
    df = df.drop('attributes',axis=1)
    
    return df


def get_table_iter(obj = str, iter_serie = pd.Series, lookup_col = 'Email__c', normalize_txt = False, step = 300):

  step = min(step, len(iter_serie))

  # - Carrega lista de valores para o loop
  if normalize_txt:
    leads_from_vendas = list(iter_serie.str.lower().drop_duplicates().values)
  else:
    leads_from_vendas = list(iter_serie.drop_duplicates().values)

  # iterando a lista de emails em batches (limitação do Salesforce)
  passo = min(step, len(leads_from_vendas))
  ls_lf = list()
  x = 0

  # log
  print('batch size:', passo)
  print('Loading batches..')
  
  for x in tqdm(range(0, len(leads_from_vendas), passo), colour='#2CD5E4'):
    ls_lf.append(get_table(obj, where = "{} IN {}".format(lookup_col, tuple(leads_from_vendas[x:x+passo])), bar=True))

  # - Concatena dados
  sf_leads = pd.concat(ls_lf, ignore_index = True)
  
  return sf_leads

def get_objects_names():
    '''Retorna pd.DataFrame() com todos os Objetos encontrados no SalesForce acessíveis via API ou Workbench'''
    try:
        objetos_sf = get_table('EntityDefinition', bar = False)
        objetos_sf = objetos_sf[['QualifiedApiName','Label']].drop_duplicates().rename(columns = {'QualifiedApiName':'Api'})
    except:
        objetos_sf = get_objects_names() 
    
    return objetos_sf


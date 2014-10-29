#!/usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------
#       Criador de Configurações - LB2-Refresh
#
#       Autor: Bernardo S E Vale
#       Data:   28/10/2014
#       email: bernardo.vale@lb2.com.br
#       LB2 Consultoria - Leading Business to the Next Level!
#-------------------------------------------------------------
import json
import os
import re
import datetime
import sys

__author__ = 'bernardovale'

#Constantes

#Pergunta binaria Yes/No
YESNO = 1
PATH = 2
IP = 3
TEXT = 4
LOG = 5
DMP = 6
SCHEMAS = 7
REMAP = 8

def isvalid_yesno(awnser):
    """
    Verifica se a resposta é válida
    :param awnser: Resposta do usuário
    :return:
    """
    x = str(awnser).capitalize()

    if x == 'Y' or x == 'Yes' or x == 'N' or x == 'No':
        return True
    else:
        return False


def isvalid_text(awnser):
    """
    Verifica se é um texto válido.
    Unica restrição é o espaçamento
    :param awnser:
    :return: bool
    """
    #Unica validação que eu preciso
    return awnser.strip() == awnser

def isvalid_schemas(awnser):
    """
    Testa se o campo dos schemas é valido
    :param awnser:
    :return:
    """
    for schemas in awnser.split(','):
        if schemas.strip() != schemas or schemas == 'SYS' or schemas == 'SYSTEM':
            return False
    return True

def isvalid_ip(awnser):
    """
    Verifica se é um IPv4 válid
    :param awnser:
    :return: bool
    """
    return bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",awnser))

def isvalid_remap(awnser):
    """
    Verifica se é um remap de datapump válido
    :param awnser:
    :return: bool
    """
    for remap in awnser.split(','):
        if not bool(re.match(r"[\S]*:[\S]*",remap)):
            return False
    return True

def isvalid_path(awnser):
    """
    Verifica se a resposta é um caminho válido
    :param awnser:
    :return: bool
    """
    fileName, fileExtension = os.path.splitext(awnser)
    return fileExtension == '.json'

def isvalid_dump(awnser):
    """
    Verifica se a resposta é um dump válido
    :param awnser:
    :return: bool
    """
    fileName, fileExtension = os.path.splitext(awnser)
    return fileExtension == '.dmp'

def isvalid_log(awnser):
    """
    Verifica se a resposta é um log válido
    :param awnser:
    :return: bool
    """
    fileName, fileExtension = os.path.splitext(awnser)
    return fileExtension == '.log'

def isvalid(awnser,type, default):
    """
    Pergunta generica
    :param awnser: Resposta
    :param type: Tipo de pergunta
    :param default: Caso tecle ENTER esta e a resposta
    :return:
    """
    if type == YESNO:
        return isvalid_yesno(awnser)
    elif type == PATH:
        return isvalid_path(awnser)
    elif type == IP:
        return isvalid_ip(awnser)
    elif type == TEXT:
        return isvalid_text(awnser)
    elif type == DMP:
        return isvalid_dump(awnser)
    elif type == LOG:
        return isvalid_log(awnser)
    elif type == SCHEMAS:
        return isvalid_schemas(awnser)
    elif type == REMAP:
        return isvalid_remap(awnser)


def hint(type):
    """
    Retorna uma dica de como responder uma pergunta do tipo enviado
    :param type:
    :return:
    """
    if type == YESNO:
        return "Responda somente YES(y) ou NO(n)"
    elif type == PATH:
        return "Este não é um JSON válido!"
    elif type == IP:
        return "Não é um IP válido!"
    elif type == TEXT:
        return "Resposta inválida, remova os espaços em branco!"
    elif type == LOG:
        return "Resposta inválida, o arquivo deve ter extensão .log!"
    elif type == DMP:
        return "Resposta inválida, o arquivo deve ter extensão .dmp!"
    elif type == SCHEMAS:
        return "Schemas inválidos, garanta que não exista espaço ou que não " \
               "tenha inserido schemas do sistema (SYS,SYSTEM)"
    elif type == REMAP:
        return "Remap inválido. Siga o padrão exemplo: TASY_DATA:TASY_DADOS,DE:PARA"

def build_question(question, type, default):
    """
    Gerencia o ciclo de vida de uma pergunta
    :param question: Pergunta
    :param type: Tipo da Pergunta
    :param default: Caso tecle ENTER esta e a resposta
    :return: Valor retornado pelo pergunta
    """
    awnser = ''
    is_valid = False
    while is_valid != True:
        awnser = raw_input(question)
        if awnser == '':
            awnser = default
            return awnser
        is_valid = isvalid(awnser, type, default)
        if not is_valid:
            print hint(type)
    return awnser

def datapump_option(datapump_dict):
    """
    Metodo dedicado para realizar o processamento
    dos opcionais do impdp
    :param datapump_dict: Dicionario com todos os opcionais
    :return: dict
    """
    more = True
    while(more):
        option = raw_input("Escolha uma opção! \n 1 - Remap User \n 2 - Remap Tablespace \n:")

        if option == '1':
            datapump_dict['remap_schema'] = build_question('Insira o remapeamento dos usuários do '
                                         'Datapump: Default('+datapump_dict['remap_schema']+'):'
                                        ' ', REMAP, datapump_dict['remap_schema'])
        elif option == '2':
            datapump_dict['remap_tablespace'] = \
                build_question('Insira o remapeamento das tablespaces do Datapump: '
                               'Default('+datapump_dict['remap_tablespace']+'): '
                               , REMAP, datapump_dict['remap_tablespace'])
        else:
            print "Escolha uma opção válida!"
        more = bool(
            build_question("Deseja adicionar outro opcional ao Datapump? [yes/no] Default(no):",YESNO,'No')
            [0].capitalize() == 'Y')
    #Faço a limpeza do dicionario, para que esse contenha somente chaves que possuam valores.
    return clean_dict(datapump_dict)

def clean_dict(my_dict):
    """
    Metodo maroto para limpar as chaves que nao possuem valores
    :param my_dict:
    :return:
    """
    for k in my_dict.keys():
        if my_dict[k] == '' or my_dict[k] == {}:
            my_dict.pop(k)
    return my_dict
def main():
    #LEITURA DO ARQUIVO DE CONFIGURAÇÃO
    destino_dict = {'sid': '', 'ip' : '', 'osuser' : '', 'senha' : ''
        , 'user' : '', 'directory' : '', 'var_dir' : ''}
    remetente_dict = {'ip': '', 'osuser' : '', 'ospwd' : '', 'backup_file' : ''}
    datapump_dict = {'remap_schema' : '', 'remap_tablespace' : ''}
    config_path =  build_question("Onde deseja gravar o arquivo de configuração '.json' ? "
                                  "Default:("+os.getcwd()+"/config.json):",PATH,""+os.getcwd()+"/config.json")

    remetente = build_question("Deseja buscar o backup em um servidor remoto? [yes/no] Default:(no): ",YESNO,'No')
    if remetente[0].capitalize() == 'Y':
        remetente_dict['ip'] = build_question('IP do servidor remoto? Default(127.0.0.1):',IP,'127.0.0.1')
        remetente_dict['osuser'] = build_question('Usuário do servidor remoto? Default(oracle):',TEXT,'oracle')
        remetente_dict['ospwd'] = build_question('Senha do Usuário do servidor remoto? Default(oracle):',TEXT,'oracle')
        remetente_dict['backup_file'] = build_question('Backup no servidor remoto? '
                    'Default(/u01/app/oracle/backup/dpfull_'+datetime.datetime.now().strftime("%Y%m%d")+'.dmp):',DMP
                    ,'/u01/app/oracle/backup/dpfull_'+datetime.datetime.now().strftime("%Y%m%d")+'.dmp')
    destino_dict['sid'] = build_question('SID do banco de dados que será atualizado. Default(oradb):'
                                         , TEXT, 'oradb')
    destino_dict['ip'] = build_question('IP do banco de dados que será atualizado. Default(127.0.0.1):'
                                         , IP, '127.0.0.1')
    destino_dict['osuser'] = build_question('Usuário do Sistema operacional do banco de dados que será atualizado.'
                                            ' Default(oracle):'
                                         , TEXT, 'oracle')
    destino_dict['ospwd'] = build_question('Senha do Usuário do Sistema operacional do banco de dados que '
                                           'será atualizado. Default(oracle):'
                                         , TEXT, 'oracle')
    destino_dict['user'] = build_question('Usuário de conexão com o banco. Default(sys):'
                                         , TEXT, 'sys')
    destino_dict['senha'] = build_question('Senha do Usuário de conexão com o banco. Default(oracle):'
                                         , TEXT, 'oracle')
    destino_dict['directory'] = build_question('Diretório do DATAPUMP. Default(DATAPUMP):'
                                         , TEXT, 'DATAPUMP')
    destino_dict['var_dir'] = build_question('Arquivo com as variáveis de ambiente. '
                                             'Default(/home/oracle/.bash_profile):'
                                         , TEXT, '/home/oracle/.bash_profile')
    backup_file = build_question('Backup a ser utilizado na importação: Default(/u01/app/oracle/backup/dpfull_'
                                 ''+datetime.datetime.now().strftime("%Y%m%d")+'.dmp):'
            , DMP, '/u01/app/oracle/backup/dpfull_'+datetime.datetime.now().strftime("%Y%m%d")+'.dmp')
    log_file = build_question('Log da importação (Datapump): Default(import_'
                                 ''+datetime.datetime.now().strftime("%Y%m%d")+'.log):'
            , LOG, 'import_'+datetime.datetime.now().strftime("%Y%m%d")+'.log')
    schemas = build_question('Lista de schemas a ser atualizados separados por vírgula: Default(TASY,TASY_VERSAO):'
    , SCHEMAS, 'TASY,TASY_VERSAO').split(',')
    print schemas
    datapump_options = build_question('Deseja inserir algum opcional no import do Datapump? [yes/no] Default:(no):'
    , YESNO, 'No')
    if datapump_options[0].capitalize() == 'Y':
        datapump_option(datapump_dict)
    config = {
        'destino' : destino_dict,
        'remetente' : clean_dict(remetente_dict),
        'backup_file' : backup_file,
        'schemas' : schemas,
        'logfile' : log_file,
        'datapump_options' : clean_dict(datapump_dict)
    }
    with open(config_path, 'w') as config_file:
        json.dump(clean_dict(config), config_file, ensure_ascii=False, indent=4, sort_keys=True)
if __name__ == '__main__':
    main()
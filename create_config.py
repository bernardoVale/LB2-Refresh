#!/usr/bin/python
#-*- coding: utf-8 -*-
# -------------------------------------------------------------
# Criador de Configurações - LB2-Refresh
#
#       Autor: Bernardo S E Vale
#       Data:   28/10/2014
#       email: bernardo.vale@lb2.com.br
#       LB2 Consultoria - Leading Business to the Next Level!
#-------------------------------------------------------------
import json
import os
import pkgutil
import re
import datetime
import socket

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
    return bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", awnser))


def isvalid_remap(awnser):
    """
    Verifica se é um remap de datapump válido
    :param awnser:
    :return: bool
    """
    for remap in awnser.split(','):
        if not bool(re.match(r"[\S]*:[\S]*", remap)):
            return False
    return True


def isvalid_path(awnser):
    """
    Verifica se a resposta é um caminho válido
    :param awnser:
    :return: bool
    """
    filename, file_extension = os.path.splitext(awnser)
    return file_extension == '.json'


def isvalid_dump(awnser):
    """
    Verifica se a resposta é um dump válido
    :param awnser:
    :return: bool
    """
    file_name, file_extension = os.path.splitext(awnser)
    return file_extension == '.dmp'


def isvalid_log(awnser):
    """
    Verifica se a resposta é um log válido
    :param awnser:
    :return: bool
    """
    file_name, file_extension = os.path.splitext(awnser)
    return file_extension == '.log'


def isvalid(awnser, my_type):
    """
    Pergunta generica
    :param awnser: Resposta
    :param my_type: Tipo de pergunta
    :return:
    """
    if my_type == YESNO:
        return isvalid_yesno(awnser)
    elif my_type == PATH:
        return isvalid_path(awnser)
    elif my_type == IP:
        return isvalid_ip(awnser)
    elif my_type == TEXT:
        return isvalid_text(awnser)
    elif my_type == DMP:
        return isvalid_dump(awnser)
    elif my_type == LOG:
        return isvalid_log(awnser)
    elif my_type == SCHEMAS:
        return isvalid_schemas(awnser)
    elif my_type == REMAP:
        return isvalid_remap(awnser)


def hint(my_type):
    """
    Retorna uma dica de como responder uma pergunta do tipo enviado
    :param my_type: Tipo da dica
    :return:
    """
    if my_type == YESNO:
        return "Responda somente YES(y) ou NO(n)"
    elif my_type == PATH:
        return "Este não é um JSON válido!"
    elif my_type == IP:
        return "Não é um IP válido!"
    elif my_type == TEXT:
        return "Resposta inválida, remova os espaços em branco!"
    elif my_type == LOG:
        return "Resposta inválida, o arquivo deve ter extensão .log!"
    elif my_type == DMP:
        return "Resposta inválida, o arquivo deve ter extensão .dmp!"
    elif my_type == SCHEMAS:
        return "Schemas inválidos, garanta que não exista espaço ou que não " \
               "tenha inserido schemas do sistema (SYS,SYSTEM)"
    elif my_type == REMAP:
        return "Remap inválido. Siga o padrão exemplo: TASY_DATA:TASY_DADOS,DE:PARA"


def build_question(question, my_type, default):
    """
    Gerencia o ciclo de vida de uma pergunta
    :param question: Pergunta
    :param my_type: Tipo da Pergunta
    :param default: Caso tecle ENTER esta e a resposta
    :return: Valor retornado pelo pergunta
    """
    awnser = ''
    is_valid = False
    while not is_valid:
        print question
        awnser = raw_input('> ')
        if awnser == '':
            awnser = default
            return awnser
        is_valid = isvalid(awnser, my_type)
        if not is_valid:
            print hint(my_type)
    return awnser


def datapump_option(datapump_dict):
    """
    Metodo dedicado para realizar o processamento
    dos opcionais do impdp
    :param datapump_dict: Dicionario com todos os opcionais
    :return: dict
    """

    more = True
    while more:
        option = raw_input("Escolha uma opção! \n 1 - Remap User \n 2 - Remap Tablespace \n:")

        if option == '1':
            datapump_dict['remap_schema'] = build_question('Insira o remapeamento dos usuários do '
                                                           'Datapump: Default(' + datapump_dict['remap_schema'] + '):'
                                                                                                                  ' ',
                                                           REMAP, datapump_dict['remap_schema'])
        elif option == '2':
            datapump_dict['remap_tablespace'] = \
                build_question('Insira o remapeamento das tablespaces do Datapump: '
                               'Default(' + datapump_dict['remap_tablespace'] + '): '
                               , REMAP, datapump_dict['remap_tablespace'])
        else:
            print "Escolha uma opção válida!"
        more = bool(
            build_question("Deseja adicionar outro opcional ao Datapump? [yes/no] Default(no):", YESNO, 'No')
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


def read_questions():
    """
    Le o .json com as perguntas e popula num dicionario
    :return: dict
    """
    questions_dict = pkgutil.get_data('utils', 'create_config_questions.json')
    return dict(json.loads(questions_dict))


def main():
    #todo: Adiciar todas as perguntas a um arquivo .properties e ler de
    # la para facilitar a visualizacao
    q = read_questions()
    #LEITURA DO ARQUIVO DE CONFIGURAÇÃO
    destino_dict = {'sid': '', 'ip': '', 'osuser': '', 'senha': ''
        , 'user': '', 'directory': '', 'var_dir': ''}
    remetente_dict = {'ip': '', 'osuser': '', 'ospwd': '', 'backup_file': ''}
    datapump_dict = {'remap_schema': '', 'remap_tablespace': ''}
    config_path = build_question("Onde deseja gravar o arquivo de configuração '.json' ? "
                                 "Default:(" + os.getcwd() + "/config.json):", PATH, "" + os.getcwd() + "/config.json")

    # PERGUNTAS REFERENTES AO REMETENTE (PRODUÇÃO)
    remetente_bkp = build_question(q['remetente_bkp']['pergunta'], YESNO, q['remetente_bkp']['default'])
    if remetente_bkp[0].capitalize() == 'N':
        remetente = build_question(q['remetente']['pergunta'], YESNO, q['remetente']['default'])
        if remetente[0].capitalize() == 'Y':
            remetente_dict['ip'] = build_question(q['remetente_ip']['pergunta'], IP, q['remetente_ip']['default'])
            remetente_dict['osuser'] = build_question(q['remetente_osuser']['pergunta'], TEXT
                                                       , q['remetente_osuser']['default'])
            remetente_dict['ospwd'] = build_question(q['remetente_ospwd']['pergunta'], TEXT,
                                                    q['remetente_ospwd']['default'])
            remetente_dict['backup_file'] = build_question(q['remetente_backup_file']['pergunta'], DMP
                                                           , q['remetente_backup_file']['default'])
    else:
        remetente_dict['ip'] = build_question(q['remetente_ip']['pergunta'], IP, q['remetente_ip']['default'])
        remetente_dict['osuser'] = build_question(q['remetente_osuser']['pergunta'], TEXT
                                                   , q['remetente_osuser']['default'])
        remetente_dict['ospwd'] = build_question(q['remetente_ospwd']['pergunta'], TEXT,
                                                  q['remetente_ospwd']['default'])
        remetente_dict['backup_file'] = build_question(q['remetente_backup_file']['pergunta'], DMP
                                                       , q['remetente_backup_file']['default'])
        remetente_dict['sid'] = build_question(q['remetente_sid']['pergunta']
                                               , TEXT, q['remetente_sid']['default'])
        remetente_dict['user'] = build_question(q['remetente_user']['pergunta']
                                                , TEXT, q['remetente_user']['default'])
        remetente_dict['senha'] = build_question(q['remetente_senha']['pergunta']
                                                 , TEXT, q['remetente_senha']['default'])
        remetente_dict['directory'] = build_question(q['remetente_directory']['pergunta'], TEXT
                                                     , q['remetente_directory']['default'])
        remetente_dict['var_dir'] = build_question(q['remetente_var_dir']['pergunta'], TEXT
                                                   , q['remetente_var_dir']['default'])

    # REFERENTES AO DESTINO (TESTE)
    destino_dict['ip'] = build_question(q['destino_ip']['pergunta'], IP, q['destino_ip']['default'])
    destino_dict['osuser'] = build_question(q['destino_osuser']['pergunta'], TEXT , q['destino_osuser']['default'])
    destino_dict['ospwd'] = build_question(q['destino_ospwd']['pergunta'], TEXT, q['destino_ospwd']['default'])
    destino_dict['sid'] = build_question(q['destino_sid']['pergunta'], TEXT, q['destino_sid']['default'])
    destino_dict['user'] = build_question(q['destino_user']['pergunta'], TEXT, q['destino_user']['default'])
    destino_dict['senha'] = build_question(q['destino_senha']['pergunta'], TEXT, q['destino_senha']['default'])
    destino_dict['directory'] = build_question(q['destino_directory']['pergunta'], TEXT
                                               , q['destino_directory']['default'])
    destino_dict['var_dir'] = build_question(q['destino_var_dir']['pergunta'], TEXT
                                               , q['destino_var_dir']['default'])
    # PERGUNTAS PADRÕES
    backup_file = build_question(q['backup_file']['pergunta'], DMP,q['backup_file']['default'])
    log_file = build_question(q['log_file']['pergunta'], LOG, q['log_file']['default'])
    schemas = build_question(q['schemas']['pergunta'], SCHEMAS, q['schemas']['default']).split(',')
    datapump_options = build_question(q['datapump_options']['pergunta'], YESNO, q['datapump_options']['default'])
    if datapump_options[0].capitalize() == 'Y':
        datapump_option(datapump_dict)
    config = {
        'destino': destino_dict,
        'remetente': clean_dict(remetente_dict),
        'backup_file': backup_file,
        'schemas': schemas,
        'logfile': log_file,
        'datapump_options': clean_dict(datapump_dict)
    }
    with open(config_path, 'w') as config_file:
        json.dump(clean_dict(config), config_file, ensure_ascii=False, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
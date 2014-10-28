#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import sys

__author__ = 'bernardovale'

#Constantes

#Pergunta binaria Yes/No
YESNO = 1
PATH = 2
IP = 3
TEXT = 4

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


def isvalid_ip(awnser):
    """
    Verifica se é um IPv4 válid
    :param awnser:
    :return:
    """
    return bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",awnser))

def isvalid_path(awnser):
    """
    Verifica se a resposta é um caminho válido
    :param awnser:
    :return:
    """
    fileName, fileExtension = os.path.splitext(awnser)
    if fileExtension == '.json':
        return True
    return False

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


def hint(type):
    """
    Retorna uma dica de como responder uma pergunta do tipo enviado
    :param type:
    :return:
    """
    if type == YESNO:
        return "Responda somente YES(y) ou NO(n)"
    elif type == PATH:
        return "Este não é um caminho válido!"
    elif type == IP:
        return "Não é um IP válido!"

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

def main():

    #LEITURA DO ARQUIVO DE CONFIGURAÇÃO
    remetente_dict = {'ip': '', 'osuser' : '', 'ospwd' : '', 'backup_file' : ''}
    config_path =  build_question("Onde deseja gravar o arquivo de configuração '.json' ? "
                                  "Default:("+os.getcwd()+"/config.json):",PATH,""+os.getcwd()+"/config.json")

    remetente = build_question("Deseja buscar o backup em um servidor remoto? [yes/no] Default:(no): ",YESNO,'Yes')
    if remetente[0].capitalize() == 'Y':
        remetente_dict['ip'] = build_question('IP do servidor remoto? Default(127.0.0.1):',IP,'127.0.0.1')
        #remetente_dict['osuser'] = build_question('Usuário do servidor remoto? Default(oracle):',TEXT,'oracle')
    print remetente
    print remetente_dict
if __name__ == '__main__':
    main()
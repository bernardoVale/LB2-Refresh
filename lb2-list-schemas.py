#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import re
import sys

__author__ = 'Bernardo Vale'
__copyright__ = 'LB2 Consultoria'
import argparse

def parse_args():
    """
    Método de analise dos argumentos do software.
    Qualquer novo argumento deve ser configurado aqui
    :return: Resultado da analise, contendo todas as variáveis resultantes
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--sid', required=True, action='store',
                        dest='sid',
                        help='SID do banco de produção. Checar tnsnames.ora!')
    parser.add_argument('--user', required=True, action='store',
                        dest='user',
                        help='Usuário do banco: sys,system etc..')
    parser.add_argument('--pwd', required=True, action='store',
                        dest='pwd',
                        help='Senha do usuário especificado!')

    p = parser.parse_args()
    return p

def main():
    args = parse_args()
    f = open('list_schema.sql')
    try:
        r = ''
        query = f.read()
        if args.user == 'sys':
            r = run_sqlplus(args.pwd,args.user,args.sid,query,True,True)
        else :
            r = run_sqlplus(args.pwd,args.user,args.sid,query,True,True)
        print clean_and_wrap(r)
    finally:
        f.close()

def clean_and_wrap(result):
    """
    Limpa o resultado e deixa bonitinho, na forma como preciso.
    :param result:
    :return:
    """
    k = result.rfind(",")
    return ''.join(('\t',result,result[:k]+"]"))

def run_sqlplus(pwd, user, sid, query, pretty, is_sysdba):
        """
        Executa um comando via sqlplus
        :param credencias: Credenciais de logon  E.g: system/oracle@oradb
        :param cmd: Query ou comando a ser executado
        :param pretty Indica se o usuário quer o resultado com o regexp
        :param Usuário é sysdba?
        :return: stdout do sqlplus
        """
        credencias = user +'/'+ pwd+'@'+sid
        if is_sysdba:
            credencias += ' as sysdba'
        session = subprocess.Popen(['sqlplus','-S',credencias], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        session.stdin.write(query)
        stdout, stderr = session.communicate()
        if pretty:
            r_unwanted = re.compile("[\n\t\r]")
            stdout = r_unwanted.sub("", stdout)
        if stderr != '':
            print stdout
            print 'ERRO - Falha ao executar o comando:'+query
            sys.exit(2)
        else:
            return stdout

if __name__ == '__main__':
    main()


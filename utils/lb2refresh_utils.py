# coding=utf-8
import json
import logging
import os
import pkgutil
import subprocess
import re


__author__ = 'bernardovale'


class RefreshUtils:
    def __init__(self):
        pass

    @staticmethod
    def run_remote_cmd(cmd, credenciais):
        HOST="root/alsk1029QWE#@10.200.0.114"
        output = ''
        command = 'ls -l'
        #run_remote(cmd=command, ip='10.200.0.114',username='root', password='alsk1029QWE#')
        # ssh = SSH(ip='10.200.0.114', password='coco', username='root')
        # ssh.connect()

    @staticmethod
    def refresh_status(mensagem):
        """
        Atualiza o status do meu arquivo de estado da atualização
        :return: None
        """
        logging.debug("Método refresh_status")
        with open('status.txt', 'w') as status_file:
            status_file.write(mensagem)

    @staticmethod
    def file_exists(path):
        """
        Garante que o arquivo existe no SO
        :param path: Path do arquivo
        :return: Afirmação
        """
        logging.debug('Método file_exists')
        logging.info('Verificando se existe o arquivo:' + path)
        # Agora tambem sei brincar de lambda
        x = lambda y: True if os.path.isfile(y) and os.access(y, os.R_OK) else False
        return x(path)

    @staticmethod
    def restarted_successful(log):
        """
        Verifica se o banco foi reiniciado com sucesso
        :param log: Log do sqlplus
        :return: bool
        """
        logging.debug("Método restarted_successful")
        is_up = lambda x: True if 'Database opened.' in x or 'aberto.' in x else False
        if is_up(log):
            logging.info("Banco reiniciado. Prosseguindo!")
            return True
        logging.error("Impossivel reiniciar o banco de dados!")
        return False

    @staticmethod
    def call_command(command):
        logging.debug("Método call_command")
        process = subprocess.Popen(command.split(' '),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        return process.communicate()

    @staticmethod
    def leave_with_message(message):
        """
        Método padronizado para finalizar o script
        :param message: Mensagem final
        :return: None
        """
        logging.debug("Método leave_with_message")
        logging.error(message)
        logging.error("Finalizando o script...")
        exit(2)

    @staticmethod
    def capped_file_path(my_file):
        """
            Método para extrair o nome do arquivo tendo o caminho completo como parametro
            :param my_file Nome completo do arquivo
            :return: file
         """
        logging.debug("Método capped_file_path")
        return os.path.basename(my_file)

    @staticmethod
    def run_sqlplus(credencias, query, pretty, is_sysdba):
        """
        Executa um comando via sqlplus
        :param query: Query ou comando a ser executado
        :param pretty: Indica se o usuário quer o resultado com o regexp
        :param is_sysdba: Usuário é sysdba?
        :return:stdout do sqlplus
        """
        logging.debug("Método run_query")
        if is_sysdba:
            credencias += ' as sysdba'
        logging.info('Abrindo conexao sqlplus com as credencias:' + credencias)
        session = subprocess.Popen(['sqlplus', '-S', credencias], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info('Executando o comando:' + query)
        session.stdin.write(query)
        stdout, stderr = session.communicate()
        if pretty:
            r_unwanted = re.compile("[\n\t\r]")
            stdout = r_unwanted.sub("", stdout)
        if stderr != '':
            logging.error(stdout)
            logging.error(stderr)
            RefreshUtils.leave_with_message('Falha ao executar o comando:' + query)
        else:
            return stdout

# coding=utf-8
import logging
from random import randint
from utils.lb2refresh_utils import RefreshUtils

__author__ = 'bernardovale'


class DatapumpDir:
    def __init__(self, config):
        """
        Arquivo de configuração Config
        :param config:
        :return:
        """
        self.config = config

    def check_dir_exists(self, path, credenciais):
        """
            Verifica se existe realmente um diretorio
            no dba_directories com o valor do config
        :param datapump_dir:
        :param credenciais: Credenciais de login
        :return: bool
        """
        logging.debug("Método check_dir_exists")
        query = "set head off; \n" \
                "set feedback off; \n" \
                "select directory_name from dba_directories" \
                " where directory_path = '%s';" % path
        logging.info("Verificando se existe o diretório %s na dba_directories" % path)
        result = RefreshUtils.run_sqlplus(credenciais, query, True, True)
        logging.info("Resultado: %s" % result)
        return result

    def create_if_dont_exists(self, path, credenciais):
        """
        Cria um diretório da DBA_DIRECTORIES se já não existir
        :param path:
        :param credenciais:
        :return:
        """
        logging.debug("Método create_if_dont_exists")
        resulted_dir = self.check_dir_exists(path, credenciais)
        if resulted_dir is '':
            logging.info("Diretório de backup inexistente, criando...")
            datapump_dir = "TEMP_DIR_%s" % str(randint(1000000000, 9999999999))
            query = "create directory " + datapump_dir + " as '%s';" % path
            resulted_dir = RefreshUtils.run_sqlplus(credenciais, query, True, True)

            if 'ORA-' in resulted_dir:
                RefreshUtils.leave_with_message("Erro ao criar diretorio: %s" % resulted_dir)
            resulted_dir = datapump_dir
        logging.info("Setando o config.directory para %s" % resulted_dir)
        self.config.directory = resulted_dir

    def check_for_imp_dir(self):
        backup_dir = RefreshUtils.only_path(self.config.backup_file) + '/'
        credencias = self.config.user + '/' + self.config.senha + '@' + self.config.sid
        self.create_if_dont_exists(backup_dir, credencias)
# coding=utf-8
import logging
from random import randint
from utils.lb2refresh_utils import RefreshUtils

__author__ = 'bernardovale'


class DatapumpDir:
    def __init__(self, config=None):
        """
        Arquivo de configuração Config
        :param config:
        :return:
        """
        self.config = config
        # Diretorio temporario criado na dba_directories
        self.temp_datapump = ''

    def drop_temp_directory(self, credenciais):
        """
        Remove o diretório criado na dba_directories
        :param credenciais: Credenciais de conexao com o banco
        :return:
        """
        if self.temp_datapump is not '':
            logging.info("Limpando diretório...")
            query = "drop directory " + self.temp_datapump + ";"
            result = RefreshUtils.run_sqlplus(credenciais, query, True, True)
            if 'ORA-' in result:
                logging.error("Atenção, impossível remover o diretório %s" % self.temp_datapump)
            else:
                logging.info("Diretório removido!")
        else:
            logging.info("Não é necessário realizar a limpeza...")

    def drop_imp_temp_directory(self):
        """
        Método para chamar o drop especifico para o banco
        que será atualizado
        :return:
        """
        logging.debug("Método drop_imp_temp_directory")
        credencias = self.config.user + '/' + self.config.senha + '@' + self.config.sid
        self.drop_temp_directory(credencias)

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
            self.temp_datapump = "TEMP_DIR_%s" % str(randint(1000000000, 9999999999))
            query = "create directory " + self.temp_datapump + " as '%s';" % path
            resulted_dir = RefreshUtils.run_sqlplus(credenciais, query, True, True)

            if 'ORA-' in resulted_dir:
                RefreshUtils.leave_with_message("Erro ao criar diretorio: %s" % resulted_dir)
            resulted_dir = self.temp_datapump
        logging.info("Setando o config.directory para %s" % resulted_dir)
        self.config.directory = resulted_dir

    def check_for_imp_dir(self):
        logging.info("Método check_for_imp_dir")
        backup_dir = RefreshUtils.only_path(self.config.backup_file) + '/'
        credencias = self.config.user + '/' + self.config.senha + '@' + self.config.sid
        self.create_if_dont_exists(backup_dir, credencias)
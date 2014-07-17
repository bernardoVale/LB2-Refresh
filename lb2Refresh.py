# coding=utf-8
__author__ = 'Bernardo Vale'
__copyright__ = 'LB2 Consultoria'

import unittest
import json
import sys
import os
import os.path
import cx_Oracle
import logging
import datetime

class Config:
    """
        Objeto de Configuração do LB2-Refresh
    """
    def wrap(self,config):
        try:
            self.sid = config['destino']['sid']
            self.ip = config['destino']['ip']
            self.user = config['destino']['user']
            self.senha = config['destino']['senha']
            self.directory = config['destino']['directory']
            self.backup_file = config['backup_file']
            self.log_dir = config['log_dir']
            self.schemas = config['schemas']
            self.coletar_estatisticas = config['coletar_estatisticas']
        except:
            print "Verifique o JSON de configuração. Declarações incorretas"
        return self


class LB2Refresh:

    def __init__(self):
        # Configuração do Log
        logging.basicConfig(filename='LB2Refresh_'+datetime.datetime.now().strftime("%Y%m%d%H%M")+'.log'
                            ,level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
        logging.info('Iniciando LB2-Refresh')
        self.config = ''
        self.readConfig(str(sys.argv[1]))

    def buildConfig(self):
        """
        Constroi um Objeto com todas as propriedades do JSON
        :return:
        """
        logging.debug('Método buildConfig')
        self.config = Config().wrap(self.config)
    def readConfig(self,path):
        '''
        Realiza a leitura do JSON e adiciona a variavel config.
        :param path: Local do json de config.
        :return: None
        '''
        logging.debug('Método readConfig')
        if self.fileExists(path):
            logging.info('Abrindo o json:'+str(path))
            loader = open(path)
            self.config = json.load(loader)
            loader.close()
        else:
            logging.error('Arquivo inexistente:'+str(path))

    def fileExists(self,path):
        '''
        Garante que o arquivo existe no SO
        :param path: Path do arquivo
        :return: Afirmação
        '''
        logging.debug('Método fileExists')
        logging.debug('Verificando se existe o arquivo:'+path)
        if os.path.isfile(path) and os.access(path, os.R_OK):
            logging.info('Existe!')
            return True
        else:
            logging.info('Não existe!')
            return False

    def estabConnection(self,c=Config):
        """
        Tenta conectar no Oracle com as credenciais
        :param c: Instancia do Arquivo de Config
        :return: Uma conexão ativa com o banco
        """
        logging.debug('Método estabConnection')
        try:
            logging.info('Tentando conectar com o banco...')
            conn = cx_Oracle.connect(c.user + '/' + c.senha + '@' + c.ip + '/' +c.sid)
        except:
            logging.error('Não foi possível estabelecer a conexão')
            logging.error(sys.exc_info()[0])
            return False
        logging.info("Conexão estabelecida!")
        return conn
    def cleanSchemas(self):
        """
        Irá remover todos os schemas do banco de dados
        Com base utilizando os nomes contidos na lista de schemas
        :return:
        """
        logging.debug("Método cleanSchemas")
        con = self.estabConnection(self.config)
        if isinstance(con,bool):
            sys.exit(2)
        cur = con.cursor()
        logging.info("Iniciando limpeza...")
        for schema in self.config.schemas:
            logging.info("Realizando limpeza do usuario "+schema)
            res  = cur.callfunc('lb2_refresh_clean', cx_Oracle.STRING, [schema])
            print res
        logging.info("Todos os usuários foram removidos do banco!")
#l = LB2Refresh()
#l.buildConfig()
#l.cleanSchemas()
#l.estabConnection(l.config)
#print l.config.backup_file
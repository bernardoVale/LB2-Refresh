#!/usr/bin/python
# -*- coding: utf-8 -*-
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
import pxssh

class Config:
    """
        Objeto de Configuração do LB2-Refresh
    """
    def __init__(self,config=None):
        try:
            self.sid = config['destino']['sid']
            self.ip = config['destino']['ip']
            self.user = config['destino']['user']
            self.senha = config['destino']['senha']
            self.directory = config['destino']['directory']
            self.backup_file = config['backup_file']
            self.log_dir = config['log_dir']
            self.schemas = config['schemas']
            self.osuser = config['destino']['osuser']
            self.ospwd = config['destino']['ospwd']
            self.var_dir = config['destino']['var_dir']
            self.coletar_estatisticas = config['coletar_estatisticas']
        except:
            pass

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
        self.config = Config(self.config)
            #.wrap(self.config)
    def readConfig(self,path):
        '''
        Realiza a leitura do JSON e adiciona a variavel config.
        :param path: Local do json de config.
        :return: None
        '''
        logging.debug('Método readConfig')
        if self.fileExists(path):
            logging.info('Abrindo o json:'+str(path))
            with open(path) as opf:
                self.config = json.load(opf)
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
        #Agora tambem sei brincar de lambda
        x = lambda y: True if os.path.isfile(y) and os.access(y, os.R_OK) else False
        return x(path)
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
    def runRemote(self,cmd):
        """
        Executa um comando no host Destino
        :param cmd: comando a ser executado (list)
        :return: Resultado do comando
        """
        result = ""
        logging.debug("Método runRemote")
        s = pxssh.pxssh()
        logging.info("Iniciando conexão SSH")
        if not s.login (self.config.ip, self.config.osuser, self.config.ospwd):
            logging.error("Falha ao realizar conexão remota:")
            logging.error("Credencias: ip:"+self.config.ip
                          +" user:"+self.config.osuser+" senha:"+self.config.ospwd)
            sys.exit(2)
        else:
            logging.info("Conexao realizada. Executando comando:"+cmd)
            s.sendline (cmd)
            s.prompt()         # match the prompt
            # Gambi pra tirar o comando que eu chamei
            result = '\n'.join(str(s.before).split('\n')[1::])
            s.logout()
        return result
        # shell = lambda a,b,c,d: spur.SshShell(hostname=a, username=b, password=b).run(d)
        # logging.info("Executando comando: "+str(cmd))
        # try:
        #     return shell(self.config.ip,self.config.osuser,self.config.ospwd,cmd).output
        # except:
        #     logging.info("Comando:"+str(cmd)+" inválido, verifique as variáveis de ambiente")
        #     sys.exit(2)
        #     pass

    def leaveWithMessage(self,message):
        """
        Método padronizado para finalizar o script
        :param message: Mensagem final
        :return: None
        """
        logging.error(message)
        logging.error("Finalizando o script...")
        sys.exit(2)

    def checkOraVariables(self):
        """
        Responsável por verificar se todas as variáveis necessárias
        a importação estão OK!

        Caso aconteça algum erro o script termina
        :return: (bool) Se estiver tudo OK
        """
        logging.debug("Método checkOraVariables")
        result = self.runRemote(". "+self.config.var_dir+";env")
        if "-bash" in result:
            self.leaveWithMessage(result)
        if "ORACLE_HOME" not in result:
            self.leaveWithMessage("ORACLE_HOME não foi setado. Verifique o arquivo:"
                          +self.config.var_dir)
        result = self.runRemote(". "+self.config.var_dir+";impdp help=y")
        if "-bash" in result:
            self.leaveWithMessage(result)
        logging.info("Tudo OK. Podemos iniciar a importação!")
        return True

# l = LB2Refresh()
# l.buildConfig()
# l.cleanSchemas()
# is_ok = l.checkOraVariables()
# if is_ok:
#     print "do_importacao"
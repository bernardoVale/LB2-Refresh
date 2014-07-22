#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse

__author__ = 'Bernardo Vale'
__copyright__ = 'LB2 Consultoria'

import json
import sys
import os
import os.path
import cx_Oracle
import logging
import datetime
import pxssh


def parse_args():
    """
    Método de analise dos argumentos do software.
    Qualquer novo argumento deve ser configurado aqui
    :return: Resultado da analise, contendo todas as variáveis resultantes
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', default=False,
                        dest='is_testing',
                        help='Realiza uma bateria de testes antes de importar.')
    parser.add_argument('--build', action='store_true', default=False,
                        dest='is_building',
                        help='Realiza todas as operações necessárias para o funcionamento\
                         do software na base destino. (EXECUTAR EM BASES QUE NUNCA UTILIZARAM O SOFTWARE)')
    parser.add_argument('--config', required=True, action='store',
                        dest='config',
                        help='Arquivo de configuração, obrigatório para o funcionamento do software.')
    #Default é o local do script
    parser.add_argument('--log', action='store',default=os.getcwd(),
                        dest='log_dir',
                        help='Diretório para salvar o log da operação.')

    parser.add_argument('--version', action='version', version='%(prog)s 1.0',
    help='Exibe a versão atual do sistema.')

    return parser.parse_args()

class Config:
    """
        Objeto de Configuração do LB2-Refresh
    """
    def __init__(self,config=None):
        #Necessário pois as vezes chamo esse método sem passar um dict
        if isinstance(config,dict):
            # Esses parametros entram no try pois são obrigatórios.
            try:
                self.sid = config['destino']['sid']
                self.ip = config['destino']['ip']
                self.user = config['destino']['user']
                self.senha = config['destino']['senha']
                self.directory = config['destino']['directory']
                self.backup_file = config['backup_file']
                self.logfile = config['logfile']
                self.schemas = config['schemas']
                self.osuser = config['destino']['osuser']
                self.ospwd = config['destino']['ospwd']
                self.var_dir = config['destino']['var_dir']
            except:
                logging.error("Falha ao ler um dos parametros."
                              " Verifique o JSON de configuração")
                sys.exit(2)
            # Variáveis opcionais
            if dict(config).has_key('coletar_estatisticas'):
                self.coletar_estatisticas = config['coletar_estatisticas']
            if dict(config).has_key('remap_tablespace'):
                self.remap_tablespace = config['remap_tablespace']

class LB2Refresh:

    def __init__(self):
        self.config = ''

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
            #So conecto com sysdba
            conn = cx_Oracle.connect(c.user + '/' + c.senha + '@' + c.ip + '/' +c.sid,mode = cx_Oracle.SYSDBA)
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
            #Necessário para pegar os prints do dbms_output
            cur.callproc("dbms_output.enable")
            res  = cur.callfunc('lb2_refresh_clean', cx_Oracle.STRING, [schema])
            #cur.callproc('where.my_package.ger_result', ['something',])
            statusVar = cur.var(cx_Oracle.NUMBER)
            lineVar = cur.var(cx_Oracle.STRING)
            while True:
                cur.callproc("dbms_output.get_line", (lineVar, statusVar))
                if statusVar.getvalue() != 0:
                    break
                logging.info(lineVar.getvalue())
            #O primeiro caracter define o sucesso.
            if res[0] == "1":
                self.leaveWithMessage(res)
            logging.info(res)
        logging.info("Todos os usuários foram removidos do banco!")

    def runRemote(self,cmd):
        """
        Executa um comando no host Destino
        :param cmd: comando a ser executado (list)
        :return: Resultado do comando
        """
        result = ""
        logging.debug("Método runRemote")
        # 48 horas
        s = pxssh.pxssh(timeout=172800, maxread=999999999)
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

    def testBackup(self):
        """
        Verifica se o backup existe.
        :return: bool
        """
        if self.fileExists(self.config.backup_file):
            logging.info("Backup existe!")
            return True
        else:
            logging.error("Backup inexistente, verifique o arquivo:"
                          +self.config.backup_file)
            return False
    def buildSchema(self):
        """
        Constroí as funções necessárias para a aplicação
        :return:
        """
        logging.debug("Método buildSchema")
        logging.info("Abrindo arquivo lb2_refresh_clean.sql")
        with open('lb2_refresh_clean.sql') as f:
            sql = f.read()
        con = self.estabConnection(self.config)
        if isinstance(con,bool):
            sys.exit(2)
        cur = con.cursor()
        cur.execute(sql)

    def runImport(self):
        """
        Roda o impdp de acordo com as especificações do Config File
        :rtype : object
        :return:
        """
        cmd = "impdp "+self.config.user+"/"+self.config.senha \
        +"@" +self.config.sid +" directory="+self.config.directory+" dumpfile="+self.config.backup_file \
        + " logfile="+self.config.logfile+" schemas=" \
        +','.join(list(self.config.schemas))
        # Adição de parametros opicionais
        if hasattr(self.config, 'remap_tablespace'):
            cmd = cmd + " remap_tablespace="+self.config.remap_tablespace
        r = self.runRemote(cmd)
        logging.info("Resultado do Import")
        logging.info(r)


def testMode(config):
    """
    Método de teste, executar antes do run()
    :param config: Arquivo JSON de Configuração
    :return: None
    """
    l = LB2Refresh()
    l.readConfig(config)
    l.buildConfig()
    if l.estabConnection(l.config):
        print "Conexão OK!"
        r = l.runRemote("echo -n teste")
        if r == "teste":
            print "Conexão SSH OK!"
            if l.checkOraVariables():
                print "Variáveis de Ambiente OK!"
            else:
                print "Erro exportando as variáveis!"
        else:
            print "Erro na conexão SSH"
    else:
        print "Erro na conexão!"

def run(config):
    """
    Método principal de execução
    :param config: Arquivo JSON de Configuração
    :return: None
    """
    l = LB2Refresh()
    l.readConfig(config)
    l.buildConfig()
    l.cleanSchemas()
    l.runImport()


def buildStuff(config):
    """
    Realiza todas operações necessárias para o funcionamento do sistema.
    :param config: Arquivo JSON de Configuração
    :return: None
    """
    l = LB2Refresh()
    l.readConfig(config)
    l.buildConfig()
    l.buildSchema()
    pass

# Isso é o método MAIN. Quem vem para executar testes unitários não passa por aqui
if __name__ == '__main__':
    r = parse_args()
    # Configuração do Log
    #todo Suporte ao windows! Tirar a /
    filename = r.log_dir +'/'+ 'LB2Refresh_'+datetime.datetime.now().strftime("%Y%m%d%H%M")+'.log'
    logging.basicConfig(filename=filename
                            ,level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
    logging.info('Iniciando LB2-Refresh')
    # Parametro de --test acionado. Apenas testar

    if r.is_testing:
        logging.info("Executando em modo --TEST")
        testMode(r.config)
    elif r.is_building:
        logging.info("Executando em modo --BUILD")
        buildStuff(r.config)
    else:
        logging.info("Executando no modo normal!")
        run(r.config)
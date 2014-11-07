# !/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import subprocess
import re

__author__ = 'Bernardo Vale'
__copyright__ = 'LB2 Consultoria'

import json
import os
import os.path
import logging
import datetime


def parse_args():
    """
    Método de analise dos argumentos do software.
    Qualquer novo argumento deve ser configurado aqui
    :return: Resultado da analise, contendo todas as variáveis resultantes
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--test', action='store_true', default=False,
                        dest='is_testing',
                        help='Realiza uma bateria de testes antes de importar.')

    parser.add_argument('--build', action='store_true', default=False,
                        dest='is_building',
                        help='Realiza todas as operações necessárias para o funcionamento ' \
                             'do software na base destino. \n (EXECUTAR EM BASES QUE NUNCA UTILIZARAM O SOFTWARE)')

    parser.add_argument('--config', required=True, action='store',
                        dest='config',
                        help='Arquivo de configuração, obrigatório para o funcionamento do software.')

    # Default é DEBUG
    parser.add_argument('--loglevel', action='store', default='DEBUG',
                        dest='loglevel',
                        help='Level de log do script. Pode ser DEBUG,INFO, WARNING ou ERROR.\n'
                             'Default: DEBUG')
    # Default é o local do script
    parser.add_argument('--log', action='store', default=os.getcwd(),
                        dest='log_dir',
                        help='Diretório para salvar o log da operação.')

    parser.add_argument('--noclean', action='store_true', default=False,
                        dest='dont_clean',
                        help='Realiza a importação sem remover os schemas do banco destino.')

    parser.add_argument('--posscript', action='store',
                        dest='pos_script',
                        help='Script .sql para executar após todos os procedimentos.')

    parser.add_argument('--coletar', action='store_true', default=False,
                        dest='coletar_estatisticas',
                        help='Realiza a coleta de estatisticas após a importação.\n Verificar o arquivo:'
                             ' coleta_estatisticas.sql')

    parser.add_argument('--sendbackup', action='store_true', default=False,
                        dest='send_backup',
                        help='Envia o .dmp para o servidor destino antes da importação. \n'
                             'OBS: No parametro "backup_file" do arquivo de configuração'
                             ' tenha certeza que \n você colocou o caminho completo'
                             ' do arquivo.\n'
                             'VERIFIQUE O ARQUIVO ''\'exemplo_com_rementente.json''\' para utilizar esta opção.\n'
                             'NECESSÁRIO FAZER A TROCA DE CHAVES DO SSH')

    parser.add_argument('--version', action='version', version='%(prog)s v2.0',
                        help='Exibe a versão atual do sistema.')
    p = parser.parse_args()
    # todo pesquisar suporte do argparse para parametros que não podem ser utilizados juntos
    # pe de macaco
    i = 0
    if p.is_building:
        i += 1
    if p.is_testing:
        i += 1
    if i > 1:
        print "Os parametros --build ou --test não podem ser utilizados juntos"
        exit(2)
    # todo melhorar essa logica barriguda
    if not any(p.loglevel in s for s in ['DEBUG', 'ERROR', 'WARNING', 'INFO']):
        print "LOGLEVEL deve ser um dos seguites: DEBUG,ERROR,WARNING ou INFO "
        exit(2)
    else:
        if p.loglevel == 'DEBUG':
            p.loglevel = logging.DEBUG
        elif p.loglevel == 'ERROR':
            p.loglevel = logging.ERROR
        elif p.loglevel == 'WARNING':
            p.loglevel = logging.WARNING
        elif p.loglevel == 'INFO':
            p.loglevel = logging.INFO
    return p


class Config:
    """
        Objeto de Configuração do LB2-Refresh
    """
    # DECLARAÇÃO DAS ANNOTATIONS
    DATA = "$DATA"
    annotations_dict = {DATA: datetime.datetime.now().strftime("%Y%m%d")}

    def __init__(self, config=None):
        # Necessário pois as vezes chamo esse método sem passar um dict
        if isinstance(config, dict):
            # Esses parametros entram no try pois são obrigatórios.
            logging.debug("Método __init__ Config")
            try:
                self.sid = config['destino']['sid']
                self.ip = config['destino']['ip']
                self.user = config['destino']['user']
                self.senha = config['destino']['senha']
                self.directory = config['destino']['directory']
                self.backup_file = self.parse_annotations(config['backup_file'])
                self.logfile = self.parse_annotations(config['logfile'])
                self.schemas = config['schemas']
                self.osuser = config['destino']['osuser']
                self.ospwd = config['destino']['ospwd']
                self.var_dir = config['destino']['var_dir']
                if 'remetente' in config:
                    self.rem_ip = config['remetente']['ip']
                    self.rem_osuser = config['remetente']['osuser']
                    self.rem_ospwd = config['remetente']['ospwd']
                    self.rem_backup_file = self.parse_annotations(config['remetente']['backup_file'])
                # Variáveis opcionais
                if 'datapump_options' in config:
                    if 'remap_tablespace' in config['datapump_options']:
                        self.remap_tablespace = config['datapump_options']['remap_tablespace']
                    if 'remap_schema' in config['datapump_options']:
                        self.remap_schema = config['datapump_options']['remap_schema']
            except (KeyError, NameError):
                logging.error("Falha ao ler um dos parametros."
                              " Verifique o JSON de configuração")
                exit(2)

    def parse_annotations(self, text):
        """
        Verifica se a variavel possui alguma annotation conhecida
        Caso tenha, substitui pelo valor da annotation
        :param text: Valor da variavel
        :return: Variavel com as substituicoes dos annotations
        """
        logging.debug("Método parse_annotations")
        for annoatition in self.annotations_dict.keys():
            if annoatition in text:
                text = str(text).replace(annoatition, self.annotations_dict[annoatition])
        return text


class LB2Refresh:
    def __init__(self):
        self.config = ''

    @staticmethod
    def refresh_status(mensagem):
        """
        Atualiza o status do meu arquivo de estado da atualização
        :return:
        """
        logging.debug("Método refresh_status")
        with open('status.txt', 'w') as status_file:
            status_file.write(mensagem)

    # noinspection PyMethodMayBeStatic
    def imported_successful(self, log):
        """
        Verifica se o datapump conseguiu importar com sucesso
        analizando o log do impdp
        :param log: Log do impdp
        :return: bool
        """
        # Abrindo lista de erros fatais
        logging.debug('Método imported_successful')
        with open('import_fatal_errors.txt', 'r') as error:
            error_list = error.read().split('\n')
        # Varrendo a lista para verificar se existe algum erro fatal
        for error in error_list:
            if error in log:
                logging.error('Erro fatal encontrado na importação. Erro encontrado:' + error)
                return False
        return True

    def build_config(self):
        """
        Constroi um Objeto com todas as propriedades do JSON
        :return:
        """
        logging.debug('Método build_config')
        self.config = Config(self.config)

    def read_config(self, path):
        """
        Realiza a leitura do JSON e adiciona a variavel config.
        :param path: Local do json de config.
        :return: None
        """
        logging.debug('Método read_config')
        if self.file_exists(path):
            logging.info('Abrindo o json:' + str(path))
            with open(path) as opf:
                try:
                    self.config = json.load(opf)
                except ValueError:
                    self.leave_with_message("Erro ao ler arquivo JSON. Verifique o conteudo do arquivo")
        else:
            logging.error('Arquivo inexistente:' + str(path))

    def send_backup(self):
        """
        Método responsável por enviar a copia do backup via scp
        do remetente para o destino
        :return:
        """
        logging.debug("Método send_backup")
        logging.info("Enviando backup...")
        cmd = 'scp ' + self.config.rem_osuser + '@' + self.config.rem_ip \
              + ':' + self.config.rem_backup_file + ' ' + self.config.backup_file
        print cmd
        r, err = self.call_command(cmd)
        if err != "":
            self.leave_with_message(err)
        logging.info("Backup enviado com sucesso!")

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

    def restart_database(self, retry_count):
        """
        Reinicia o banco de dados. Caso falha tenta de novo ate o limite do retry_count
        :param retry_count: Caso falhe, quantas vezes ainda posso tentar
        :return:
        """
        shutdown_query = "shutdown abort; \n" \
                         "startup; \n"
        logging.debug("Método restart_database")
        while retry_count > 0:
            logging.info("Parando o banco de dados...")
            r = self.run_sqlplus(shutdown_query, False, True)
            logging.info(r)
            if self.restarted_successful(r):
                return True
            else:
                logging.info("Falha ao reiniciar, tentando novamente...")
                retry_count -= 1
        return False

    def clean_schemas(self):
        """
        Irá remover todos os schemas do banco de dados
        Com base utilizando os nomes contidos na lista de schemas
        :return:
        """
        logging.debug("Método clean_schemas")
        retry_count = 3
        x = lambda y: True if 'Resultado:0:' in y else False
        if not self.restart_database(retry_count):
            self.leave_with_message("Impossivel reiniciar o banco de dados apos "
                                    "" + str(retry_count) + " tentativa(s). Contacte o DBA.")
        for schema in self.config.schemas:
            logging.info("Realizando limpeza do usuario " + schema)
            sql = "set serveroutput on; \n" \
                  "declare \n" \
                  "r varchar2(4000); \n" \
                  "begin \n" \
                  "r := lb2_refresh_clean('" + schema + "'); \n" \
                                                        "dbms_output.put_line('Resultado:' || r); \n" \
                                                        "end; \n" \
                                                        "/"
            r = self.run_sqlplus(sql, True, True)
            logging.info(r)
            if x(r):
                logging.info("Usuario " + schema + " removido com sucesso")
            else:
                self.leave_with_message("Impossivel remover o usuario " + schema + " finalizando...")
        logging.info("Todos os usuários foram removidos do banco!")

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

    def check_ora_variables(self):
        """
        Responsável por verificar se todas as variáveis necessárias
        a importação estão OK! Verificando as variáveis de ambinete
        Tenha certeza que o ambiente contem todas as variaveis necessárias

        Caso aconteça algum erro o script termina
        :return: (bool) Se estiver tudo OK
        """
        logging.debug("Método check_ora_variables")
        command = "env"
        result = self.call_command(command)
        result = ''.join(result)
        if "-bash" in result:
            self.leave_with_message(result)
        if "ORACLE_HOME" not in result:
            self.leave_with_message("ORACLE_HOME nao foi setado. Verifique o arquivo:"
                                    + self.config.var_dir)
        result = self.call_command("impdp help=y")
        if "-bash" in result:
            self.leave_with_message(result)
        logging.info("Tudo OK. Podemos iniciar a importação!")
        return True

    def test_backup(self):
        """
        Verifica se o backup existe.
        :return: bool
        """
        logging.debug("Método test_backup")
        if self.file_exists(self.config.backup_file):
            logging.info("Backup existe!")
            return True
        else:
            logging.error("Backup inexistente, verifique o arquivo:"
                          + self.config.backup_file)
            return False

    def test_conn(self):
        """
        Teste de conexão e credenciais
        :return:
        """
        logging.debug("Método test_conn")
        query = 'set head off \n' \
                'select 1+1 from dual;'
        result = self.run_sqlplus(query, True, True)
        logging.info(result)
        if 'ORA-' in result:
            return False
        else:
            return True

    def run_coleta_estatisticas(self):
        """
        Executa a coleta de estatisticas na base destino.
        :return:
        """
        logging.debug("Método run_coleta_estatisticas")
        logging.info("Abrindo arquivo coleta_estatisticas_v2.sql")
        with open('coleta_estatisticas_v2.sql') as f:
            sql = f.read()
        result = self.run_sqlplus(sql, False, True)
        logging.info(result)
        if 'ORA-' in result:
            self.leave_with_message("Erros ao coletar as estatisticas!")
        logging.info("Coleta de estatisticas executado com sucesso!")

    def run_sqlplus(self, query, pretty, is_sysdba):
        """
        Executa um comando via sqlplus
        :param query: Query ou comando a ser executado
        :param pretty: Indica se o usuário quer o resultado com o regexp
        :param is_sysdba: Usuário é sysdba?
        :return:stdout do sqlplus
        """
        logging.debug("Método run_sqlplus")
        credencias = self.config.user + '/' + self.config.senha + '@' + self.config.sid
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
            self.leave_with_message('Falha ao executar o comando:' + query)
        else:
            return stdout

    def check_procs(self):
        """
        Verifica se existe a procedure no banco.
        :return:
        """
        logging.debug("Método check_procs")
        query = 'set head off \n' \
                'select status from dba_objects where object_name=\'LB2_REFRESH_CLEAN\';'
        result = self.run_sqlplus(query, True, True)
        if result == 'VALID':
            logging.info("Procedure LB2_REFRESH_CLEAN criada com sucesso!")
            return True
        logging.error("Procedure LB2_REFRESH_CLEAN inexistente no banco. Execute o modo --build novamente")
        logging.error(result)
        return False

    def build_schema(self):
        """
        Constroí as funções necessárias para a aplicação
        :return:
        """
        logging.debug("Método build_schema")
        logging.info("Abrindo arquivo lb2_refresh_clean.sql")
        with open('lb2_refresh_clean_v2.sql') as f:
            sql = f.read()
        result = self.run_sqlplus(sql, False, True)
        logging.info(result)
        if self.check_procs():
            print "Build realizado com sucesso!"

    def run_pos_script(self, script):
        """
        Executa um script .sql passado como parametro
        :return:
        """
        logging.debug("Método run_pos_script")
        logging.info("Abrindo arquivo " + script)
        with open(script) as f:
            sql = f.read()
        result = self.run_sqlplus(sql, False, True)
        logging.info(result)
        if 'ORA-' in result:
            logging.error(result)
            self.leave_with_message("Erro ao executar o script:" + script)
        logging.info("Pos script executado com sucesso!")

    def run_import(self):
        """
        Roda o impdp de acordo com as especificações do Config File
        :rtype : object
        :return:
        """
        logging.debug("Método run_import")
        cmd = "impdp '" + self.config.user + "/" + self.config.senha \
              + "@" + self.config.sid + " AS SYSDBA' " \
                                        "directory=" + self.config.directory + " dumpfile=" \
              + self.capped_file_path(self.config.backup_file) + "" \
                                                                 " logfile=" + self.config.logfile + " schemas=" \
              + ','.join(list(self.config.schemas))
        # # Adição de parametros opicionais
        if hasattr(self.config, 'remap_tablespace'):
            cmd = cmd + " remap_tablespace=" + self.config.remap_tablespace
        if hasattr(self.config, 'remap_schema'):
            cmd = cmd + " remap_schema=" + self.config.remap_schema
        err, r = self.call_command(cmd)
        if err != "":
            self.leave_with_message(err)
        if not self.imported_successful(r):
            self.leave_with_message(r)
        logging.info("Resultado do Import")
        logging.info(r)

    def recompile(self):
        logging.debug("Método recompile")
        logging.info("Realizando a recompilação dos objetos...")
        query = '@$ORACLE_HOME/rdbms/admin/utlrp.sql'
        result = self.run_sqlplus(query, False, True)
        logging.info(result)

    @staticmethod
    def capped_file_path(my_file):
        """
            Método para extrair o nome do arquivo tendo o caminho completo como parametro
            :param my_file Nome completo do arquivo
            :return: file
         """
        logging.debug("Método capped_file_path")
        return os.path.basename(my_file)


def test_mode(config):
    """
    Método de teste, executar antes do run()
    :param config: Arquivo JSON de Configuração
    :return: None
    """
    logging.debug("Método test_mode")
    l = LB2Refresh()
    l.read_config(config)
    l.build_config()
    if l.test_conn():
        print "Conexão sqlplus OK!"
        r, err = l.call_command('echo -n teste')
        if r == "teste" and err == "":
            print "Chamada ao bash OK!"
            if l.check_ora_variables():
                print "Variáveis de Ambiente OK!"
            else:
                print "Erro exportando as variáveis!"
        else:
            print "Erro na chamada do bash"
    else:
        print "Erro na conexão com o sqlplus!"


def run(config, dont_clean, send_backup, coletar_estatisticas, pos_script):
    """
    Método principal de execução
    :param config: Arquivo JSON de Configuração
    :param dont_clean: Especifica se devo chamar o método clean_schemas
    :param send_backup: Especifica se é necessário enviar o backup ao destino.
    :param coletar_estatisticas: Especifica se deve realizar coleta de estatisticas
    :param pos_script: Script para ser executado após o script.
    :return: None
    """
    logging.debug("Método run")
    l = LB2Refresh()
    l.refresh_status("EM ANDAMENTO - INTERPRETANDO .JSON")
    l.read_config(config)
    l.build_config()
    if send_backup:
        l.refresh_status("EM ANDAMENTO - ENVIANDO BACKUP PARA O SERVIDOR DE TESTES")
        l.send_backup()
    if not dont_clean:
        # Então limpe
        l.refresh_status("EM ANDAMENTO - LIMPANDO OS DADOS DO BANCO DE TESTES")
        l.clean_schemas()
    l.refresh_status("EM ANDAMENTO - ATUALIZANDO OS USUARIOS")
    l.run_import()
    l.refresh_status("EM ANDAMENTO - RECOMPILANDO OS OBJETOS")
    l.recompile()
    if coletar_estatisticas:
        l.refresh_status("EM ANDAMENTO - REALIZANDO COLETA DE ESTATISITCAS")
        l.run_coleta_estatisticas()
    if pos_script is not None:
        l.refresh_status("EM ANDAMENTO - EXECUTANDO POS SCRIPT")
        l.run_pos_script(pos_script)
    l.refresh_status("LB2 REFRESH FINALIZADO!")


def build_stuff(config):
    """
    Realiza todas operações necessárias para o funcionamento do sistema.
    :param config: Arquivo JSON de Configuração
    :return: None
    """
    logging.debug("Método build_stuff")
    l = LB2Refresh()
    l.read_config(config)
    l.build_config()
    l.build_schema()


def main():
    r = parse_args()
    # Configuração do Log
    # todo Suporte ao windows! Tirar a /
    filename = r.log_dir + '/' + 'LB2Refresh_' + datetime.datetime.now().strftime("%Y%m%d%H%M") + '.log'
    logging.basicConfig(filename=filename
                        , level=r.loglevel,
                        format='%(asctime)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
    logging.info('Iniciando LB2-Refresh')
    # Parametro de --test acionado. Apenas testar
    if r.is_testing:
        logging.info("Executando em modo --TEST")
        test_mode(r.config)
    elif r.is_building:
        logging.info("Executando em modo --BUILD")
        build_stuff(r.config)
    else:
        logging.info("Executando no modo normal!")
        run(r.config, r.dont_clean, r.send_backup, r.coletar_estatisticas, r.pos_script)

# Isso é o método MAIN. Quem vem para executar testes unitários não passa por aqui
if __name__ == '__main__':
    main()